import json
import asyncio
import time
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Game
from . import game_logic

class GameConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for handling Pong game sessions.
    This consumer handles the communication aspects while delegating game logic
    to the game_logic module.
    """
    
    async def connect(self):
        """Handle WebSocket connection and authentication"""
        # Get game ID from URL route
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_group = f"game_{self.game_id}"
        
        # Get user from scope
        self.user_id = self.scope.get('user_id')
        
        if not self.user_id:
            print("User not authenticated")
            await self.close(code=4001)
            return
        
        # Get game from database
        self.game = await self.get_game(self.game_id)
        if not self.game:
            print(f"Game {self.game_id} not found")
            await self.close(code=4004)
            return
        
        # Determine if user is player1 or player2
        if str(self.user_id) == str(self.game['player1_id']):
            self.player_num = 1
        elif str(self.user_id) == str(self.game['player2_id']):
            self.player_num = 2
        else:
            print(f"User {self.user_id} is not a player in game {self.game_id}")
            await self.close(code=4003)
            return
        
        # Initialize game state if not exists
        if self.game_id not in game_logic.active_games:
            await self.initialize_game_state()
        
        # Join game group
        await self.channel_layer.group_add(
            self.game_group,
            self.channel_name
        )
        
        # Mark player as connected
        connection_info = game_logic.set_player_connection(self.game_id, self.player_num, True)
        
        # Accept connection
        await self.accept()
        
        # Send initial state and connection confirmation
        await self.send_json({
            'type': 'connection_established',
            'player_number': self.player_num,
            'game_id': self.game_id
        })
        
        await self.send_json({
            'type': 'game_state',
            'state': game_logic.active_games[self.game_id]
        })
        
        # Notify other player about connection
        await self.channel_layer.group_send(
            self.game_group,
            {
                'type': 'player_status',
                'player': self.player_num,
                'connected': True
            }
        )
        
        # If connection changed game status, notify both players
        if connection_info and connection_info['status_changed']:
            await self.channel_layer.group_send(
                self.game_group,
                {
                    'type': 'game_status_changed',
                    'status': connection_info['new_status']
                }
            )
        
        # If both players connected, start game loop if not already running
        if connection_info and connection_info['both_connected']:
            if (game_logic.active_games[self.game_id]['game_status'] == 'menu' and
                not game_logic.active_games[self.game_id].get('loop_running', False)):
                
                game_logic.active_games[self.game_id]['loop_running'] = True
                asyncio.create_task(self.game_loop())
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'game_id') and self.game_id in game_logic.active_games:
            # Mark player as disconnected
            connection_info = game_logic.set_player_connection(self.game_id, self.player_num, False)
            
            # Notify other player
            await self.channel_layer.group_send(
                self.game_group,
                {
                    'type': 'player_status',
                    'player': self.player_num,
                    'connected': False
                }
            )
            
            # If connection changed game status, notify both players
            if connection_info and connection_info['status_changed']:
                await self.channel_layer.group_send(
                    self.game_group,
                    {
                        'type': 'game_status_changed',
                        'status': connection_info['new_status'],
                        'reason': f'Player {self.player_num} disconnected'
                    }
                )
            
            # Leave game group
            await self.channel_layer.group_discard(
                self.game_group,
                self.channel_name
            )
            
            # If both players disconnected and game is over, save results and clean up
            if connection_info and not connection_info['any_connected']:
                game_status = game_logic.active_games[self.game_id]['game_status']
                if game_status in ['gameOver', 'matchOver']:
                    # Save results
                    await game_logic.save_game_results(self.game_id)
                    
                    # Clean up
                    del game_logic.active_games[self.game_id]
    
    async def receive_json(self, content):
        """Handle messages from client"""
        try:
            message_type = content.get('type', '')
            
            if message_type == 'paddle_move':
                # Update paddle position
                position = content.get('position', 0)
                
                # Update using game logic module
                success = game_logic.update_paddle_position(self.game_id, self.player_num, position)
                
                if success:
                    # Broadcast update to both players
                    await self.channel_layer.group_send(
                        self.game_group,
                        {
                            'type': 'paddle_position',
                            'player': self.player_num,
                            'position': position
                        }
                    )
            
            elif message_type == 'start_game':
                # Only proceed if game is in menu state
                if (self.game_id in game_logic.active_games and 
                    game_logic.active_games[self.game_id]['game_status'] == 'menu'):
                    
                    # Start the game
                    game_logic.set_game_status(self.game_id, 'playing')
                    
                    # Start game loop if not running
                    if not game_logic.active_games[self.game_id].get('loop_running', False):
                        game_logic.active_games[self.game_id]['loop_running'] = True
                        asyncio.create_task(self.game_loop())
                    
                    # Notify players
                    await self.channel_layer.group_send(
                        self.game_group,
                        {
                            'type': 'game_status_changed',
                            'status': 'playing'
                        }
                    )
            
            elif message_type == 'toggle_pause':
                # Only players can pause/unpause
                if self.game_id in game_logic.active_games:
                    current_status = game_logic.active_games[self.game_id]['game_status']
                    
                    if current_status == 'playing':
                        # Pause the game
                        game_logic.set_game_status(self.game_id, 'paused')
                        new_status = 'paused'
                    elif current_status == 'paused':
                        # Resume the game
                        game_logic.set_game_status(self.game_id, 'playing')
                        new_status = 'playing'
                    else:
                        return
                    
                    # Notify players
                    await self.channel_layer.group_send(
                        self.game_group,
                        {
                            'type': 'game_status_changed',
                            'status': new_status
                        }
                    )
            
            elif message_type == 'next_match':
                # Only in matchOver state
                if (self.game_id in game_logic.active_games and
                    game_logic.active_games[self.game_id]['game_status'] == 'matchOver'):
                    
                    # Reset for next match
                    game_logic.reset_for_new_match(self.game_id)
                    
                    # Notify players
                    await self.channel_layer.group_send(
                        self.game_group,
                        {
                            'type': 'game_state',
                            'state': game_logic.active_games[self.game_id]
                        }
                    )
            
            elif message_type == 'restart_game':
                # Only in gameOver state
                if (self.game_id in game_logic.active_games and
                    game_logic.active_games[self.game_id]['game_status'] == 'gameOver'):
                    
                    # Reset entire game
                    game_logic.reset_game(self.game_id)
                    
                    # Notify players
                    await self.channel_layer.group_send(
                        self.game_group,
                        {
                            'type': 'game_state',
                            'state': game_logic.active_games[self.game_id]
                        }
                    )
        
        except Exception as e:
            print(f"Error processing message: {str(e)}")
    
    async def game_loop(self):
        """Main game loop running on the server"""
        try:
            while self.game_id in game_logic.active_games:
                # Only update if game is playing
                if game_logic.active_games[self.game_id]['game_status'] == 'playing':
                    # Calculate time delta
                    current_time = time.time()
                    delta_time = current_time - game_logic.active_games[self.game_id]['last_update_time']
                    game_logic.active_games[self.game_id]['last_update_time'] = current_time
                    
                    # Update game physics
                    score_happened = game_logic.update_game_physics(self.game_id, delta_time)
                    
                    # If a score happened, check if match ended
                    if score_happened:
                        match_ended = game_logic.check_match_end(self.game_id)
                        
                        # If match ended, notify players of new status
                        if match_ended:
                            await self.channel_layer.group_send(
                                self.game_group,
                                {
                                    'type': 'game_status_changed',
                                    'status': game_logic.active_games[self.game_id]['game_status'],
                                    'winner': game_logic.active_games[self.game_id]['winner']
                                })
                        # Broadcast updated state
                    await self.channel_layer.group_send(
                        self.game_group,
                        {
                            'type': 'game_state',
                            'state': game_logic.active_games[self.game_id]
                        }
                    )
                
                # Sleep to maintain consistent frame rate
                await asyncio.sleep(1/60)  # 60 FPS
                
                # Check if game is over and no players are connected
                if self.game_id in game_logic.active_games:  # Double-check in case it was deleted
                    if not game_logic.is_any_player_connected(self.game_id):
                        game_status = game_logic.active_games[self.game_id]['game_status']
                        if game_status in ['gameOver', 'matchOver']:
                            # Save results
                            await game_logic.save_game_results(self.game_id)
                            
                            # Clean up
                            del game_logic.active_games[self.game_id]
                            break
        
        except Exception as e:
            print(f"Error in game loop: {str(e)}")
        finally:
            # Mark loop as not running
            if self.game_id in game_logic.active_games:
                game_logic.active_games[self.game_id]['loop_running'] = False
    
    # Message handlers
    
    async def game_state(self, event):
        """Send game state to client"""
        await self.send_json(event)
    
    async def paddle_position(self, event):
        """Send paddle position update"""
        await self.send_json(event)
    
    async def game_status_changed(self, event):
        """Send game status update"""
        await self.send_json(event)
    
    async def player_status(self, event):
        """Send player connection status"""
        await self.send_json(event)
    
    # Database methods
    
    @database_sync_to_async
    def get_game(self, game_id):
        """Get game from database"""
        try:
            game = Game.objects.get(id=game_id)
            return {
                'id': game.id,
                'player1_id': game.player1_id,
                'player2_id': game.player2_id,
                'status': game.status,
                'difficulty': game.difficulty
            }
        except Game.DoesNotExist:
            return None
    
    @database_sync_to_async
    def initialize_game_state(self):
        """Create initial game state in memory"""
        if self.game_id in game_logic.active_games:
            return
        
        # Get game from database and create state
        game_logic.active_games[self.game_id] = game_logic.create_game_state(
            self.game_id, 
            self.game
        )