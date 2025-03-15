"use client";

import { Progress } from "@/components/ui/progress";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { UseUser } from "@/api/get-user";

export default function cover() {
  const { data: myUserData } = UseUser();

  if (!myUserData) return <></>;

  return (
    <div className="relative w-full min-h-[30%] rounded-2xl bg-cover  backdrop-blur-sm bg-center flex flex-col justify-center items-center">
      <div className="absolute -z-10 inset-0 w-full h-full bg-black/70 rounded-2xl"></div>
      <div className="w-[50%] h-[70%]">
        <div className="flex justify-center items-center h-[75%]">
          <Avatar className="h-28 w-28">
            <AvatarImage src={myUserData.avatar} alt="profile image" className="h-full w-full" />
            zinc
            <AvatarFallback>KA</AvatarFallback>
          </Avatar>
        </div>
        <div className="flex justify-center items-center">
          {myUserData.username}
        </div>
      </div>

      <div className=" w-[80%] h-[30%]">
        <div className="space-y-4">
          {myUserData.level || "Level 0"}
          <Progress value={60} />
        </div>
      </div>
    </div>
  );
}
