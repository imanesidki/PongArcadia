"use client";

// import { UseUser } from "@/api/get-user";
import { Icon } from "@iconify/react/dist/iconify.js";
// import { Avatar, AvatarFallback, AvatarImage } from "@radix-ui/react-avatar";
import React from "react";
// import { FriendsProps } from "../page";
import { UseBlocked } from "@/api/get-blocked";
import { useFriendMutation } from "@/hooks/useFriendMutation";

export default function Blocked() {
  const { data: blockedUsers } = UseBlocked();
  const friendMutation = useFriendMutation();

  const handleUnBlockUser = (username: string) => {
    friendMutation.mutate({
      url: "/api/friends/unblock/",
      username: username,
    });
  };

  if (!blockedUsers || blockedUsers?.length === 0) {
    return (
      <div className="flex flex-col justify-center items-center h-full w-full p-6 text-center">
        <div className="bg-[#2D2A2A]/40 backdrop-blur-sm rounded-xl p-8 flex flex-col items-center max-w-md">
          <h3 className="text-2xl font-medium text-white mb-2">
            No Blocked Users
          </h3>
          <p className="text-white/70 mb-4">
            Your blocked users list is currently empty.
          </p>
          <div className="w-full h-0.5 bg-gradient-to-r from-transparent via-white/30 to-transparent rounded-full my-2" />
          <p className="text-white/50 text-sm mt-2">let it empty :P</p>
        </div>
      </div>
    );
  }

  return (
    <div className="white h-full w-full space-y-8 flex justify-center flex-col items-center">
      <div className="overflow-auto scrollbar-hide h-[90%] w-full md:w-[85%]">
        {blockedUsers.map((item) => (
          <div
            key={item.username}
            className="relative flex flex-col sm:flex-row items-center p-2 sm:p-4 mb-3 rounded-lg bg-black"
          >
            <img
              src={item.avatar}
              className="rounded-full object-cover w-16 h-16 sm:w-20 sm:h-20"
            />
            <div className="mt-2 sm:mt-0 sm:ml-4 flex-1 text-center sm:text-left">
              <div>
                <h1 className="text-base sm:text-lg text-gray-300 font-extralight">
                  {item.username}
                </h1>
              </div>
              <div className="flex flex-row justify-center sm:justify-start space-x-1 text-white">
                <h2 className="text-sm sm:text-base">{item.first_name}</h2>
                <h3 className="text-sm sm:text-base">{item.last_name}</h3>
              </div>
            </div>
            <div className="relative sm:absolute right-0 sm:right-5 mt-2 sm:mt-0 top-auto sm:top-1/2 transform sm:-translate-y-1/2 flex items-center gap-2 sm:gap-3">
              <button
                onClick={() => handleUnBlockUser(item.username)}
                className="px-2 sm:px-4 py-1 sm:py-2 text-sm sm:text-base bg-[#40CFB7]/20 text-[#40CFB7] rounded-lg hover:bg-[#40CFB7]/30 transition-all"
              >
                Unblock
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
