"use client";

import { UseUser } from "@/api/get-user";
import { Icon } from "@iconify/react/dist/iconify.js";
import { Avatar, AvatarFallback, AvatarImage } from "@radix-ui/react-avatar";
import React from "react";

const list = [
  {
    firstname: "kawtar ",
    lastname: "aboussi",
    username: "ka",
    avatar: "/assets/images/logo.svg",
  },
  {
    firstname: "kawtar ",
    lastname: "aboussi",
    username: "kaboussi",
    avatar: "/assets/images/logo.svg",
  },
  {
    firstname: "kawtar ",
    lastname: "aboussi",
    username: "ussi",
    avatar: "/assets/images/logo.svg",
  },
  {
    firstname: "kawtar ",
    lastname: "aboussi",
    username: "aboussi",
    avatar: "/assets/images/logo.svg",
  },
];

export default function Friendchat() {
  // const {data: myUserData} = UseUser()

  // if (!myUserData) return <></>;

  return (
    <div className="p-4 w-full space-y-8 flex justify-center flex-col items-center">
      <div className="flex justify-center font-bold items-center p-5">
        <p>3shrani</p>
      </div>
      <div className=" max-h-screen w-[85%]">
        {list.map((item) => (
          <div
            key={item.username}
            className="relative flex items-center p-4 mb-3  rounded-full bg-black"
          >
            <img
              src={item.avatar}
              className="rounded-full red object-cover size-20"
            />
            <div className="ml-4">
              <div>
                <h1 className="text-lg font-extralight">{item.username}</h1>
              </div>
              <div className="flex flex-row space-x-1">
                <h2>{item.firstname}</h2>
                <h3>{item.lastname}</h3>
              </div>
            </div>
            <Icon
              icon="token:chat"
              width="50"
              height="50"
              className="absolute right-5 top-1/2 transform -translate-y-1/2 text-white"
            />
          </div>
        ))}
      </div>
      <button className="border text-black p-4 bg-[#40CFB7] border-[#40CFB7] lg:w-[50%] rounded-full">
        show more ...
      </button>
    </div>
  );
}
