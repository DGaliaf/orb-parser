import asyncio
import re

import requests
import json

from utils import append_file

dev_com_id = "64eb8f1ffe0d35e52846c5ad"

#TODO: Recursive parsing
#

class UserData():
    def __init__(self, id: str, name: str, handle: str):
        self.id: str = id
        self.name: str = name
        self.handle: str = handle

    def __str__(self):
        return f"ID: {self.id} | NAME: {self.name} | HANDLE: {self.handle}"


class UserInfo():
    def __init__(self, name: str, bio: str, wallet: str, links: list, handles: list[dict]):
        self.name: str = name
        self.bio: str = bio
        self.wallet: str = wallet
        self.links: list = links
        self.handles: list[dict] = handles

    def __str__(self):
        handle_str: str = ""
        for handle in self.handles:
            handle_str += f"{handle.get("local_name")}.{handle.get("tld")}\n"

        return f"""
        NAME: {self.name}
        WALLET: {self.wallet}
        -----------------------------
        HANDLES:
        {handle_str}
        -----------------------------
        LINKS:
        {self.links}
        -----------------------------
        BIO:
        {self.bio}
        -----------------------------
        """


class OrbParser:
    def __init__(self):
        self.__headers: dict = self.__gen_headers(
            bearer_token='Bearer L2GrSHs7HRVUzN555rdfCnZ8XgANnsuwoBVE4ZaWKYeiBitwfvrHMwfFaLNTehueAe6dnqqvMYiAfba5KzhSEcbg3fxwdHLGKji7KYsAsVF5B6RGQHFWHy2DjjPcnWHC')

        self.orb_urls: dict = {
            "getProfile": "https://us-central1-stellar-verve-314311.cloudfunctions.net/ORBV2-MAINNET-get-profile",
            "getUsers": "https://us-central1-stellar-verve-314311.cloudfunctions.net/ORBV2-MAINNET-get-members",
            "getUserFriends": "https://us-central1-stellar-verve-314311.cloudfunctions.net/ORBV2-MAINNET-get-user-friends"
        }

    def __isEligibleUser(self, userInfo: UserInfo) -> bool:
        def __hasNeededBio() -> bool:
            if re.search(
                    'dev|developer|Developer|Dev|Solidity|Engineer|engineer|solidity|learn|backend|Backend|Frontend|frontend|manager|moderator|mod|content|Content|Manager',
                    "" if userInfo.bio is None else userInfo.bio):
                return True

        def __hasNeededLink() -> bool:
            if userInfo.links is not None:
                for link in userInfo.links:
                    if "." in link.get("url"):
                        return True

        if __hasNeededBio() or __hasNeededLink():
            return True

        return False

    def __gen_headers(self, bearer_token: str) -> dict:
        return {
            'Host': 'us-central1-stellar-verve-314311.cloudfunctions.net',
            'Accept': '*/*',
            'baggage': 'sentry-environment=production,sentry-public_key=159bf4c781277a30bfed3acc4690eada,sentry-release=2.1.30,sentry-trace_id=4dce4631155b4e519c44e9fc8ef54ee1',
            'orb-access-token': bearer_token,
            'orb-user': '0x08188d',
            'Authorization': bearer_token,
            'Accept-Language': 'ru',
            'orb-app-version': '2.1.30',
            'sentry-trace': '4dce4631155b4e519c44e9fc8ef54ee1-641c59c6635d4a2f-0',
            'User-Agent': 'Orb/2887 CFNetwork/1568.100.1 Darwin/24.0.0',
            'Connection': 'keep-alive',
            'x-access-token': bearer_token,
            'Content-Type': 'application/json'
        }

    async def __get_user_info(self, user: UserData) -> UserInfo | None:
        payload = json.dumps({
            "profileId": user.id,
            "handle": user.handle,
            "userAvatarThumbnailDimension": 768,
            "mediaThumbnailDimension": 1180,
            "publicationId": None
        })

        await self.__get_user_friends(user_id=user.id)

        response: dict = requests.post(self.orb_urls.get("getProfile"), headers=self.__headers, data=payload).json()

        if response.get("status") == "SUCCESS":
            r_data: dict = response.get("data")

            user_info: UserInfo = UserInfo(r_data.get("name"), r_data.get("bio"), r_data.get("ownedBy"),
                                           r_data.get("links"),
                                           r_data.get("handles"))

            return user_info
        else:
            print(f"[-] Error in gathering user info | {response.get("status")}")
            return None

    async def __get_user_friends(self, user_id: str) -> None:

        payload = json.dumps({
            "category": "followers",
            "tag": "allFollowers",
            "profileId": user_id,
            "userAvatarThumbnailDimension": 128,
            "skip": 0,
            "limit": 50
        })

        # response = requests.post(self.orb_urls.get("getUserFriends"), headers=self.__headers, data=payload).json()

        # if response.get("status") == "SUCCESS":
        #     user_friends: list[dict] = response.get("data")

            # for friend in user_friends:
            #     if friend.get("id") is None:
            #         pass

                # await append_file("results/to_parse.txt", str(friend.get("id") + "\n"))

    async def __parse_users(self) -> None:
        skip = 0

        while skip != -1:
            print(f"[???] Skip - {skip + 1}")

            payload = json.dumps({
                "category": "all",
                "tag": None,
                "communityId": dev_com_id,
                "userAvatarThumbnailDimension": 128,
                "skip": skip,
                "limit": 50
            })

            response: dict = requests.post(self.orb_urls.get("getUsers"), headers=self.__headers, data=payload).json()

            if response.get("status") == "SUCCESS":
                community_users: dict = response.get("data")[2]

                if community_users.get("pageInfo").get("next") is None:
                    break

                skip: int = int(community_users.get("pageInfo").get("next"))

                total_user_count: int = community_users.get("total")
                cur_user_count: int = 1
                print(f"[+] Total Users - {total_user_count}")

                for user in community_users.get("items"):
                    print(f"[+] [{cur_user_count}/{total_user_count}] User collected")

                    user_data: UserData = UserData(user.get("id"), user.get("name"), user.get("handle"))
                    user_info: UserInfo = await self.__get_user_info(user_data)

                    file_content: str = f"{user_info.name} | {user_info.handles} | {user_info.wallet} | {user_info.links} | {user_info.bio}\n"
                    if self.__isEligibleUser(user_info):
                        await append_file("results/eligible.txt", file_content)
                    else:
                        await append_file("results/noteligible.txt", file_content)

                    cur_user_count += 1
            else:
                print(response)
                print(f"[-] Error in calling API | {response.get("status")}")

        print("[+] Parsing end")

    async def start_parse(self) -> None:
        await self.__parse_users()


class LensParser:
    def __init__(self, orbParser: OrbParser):
        self.orbParser: OrbParser = orbParser


async def main() -> None:
    parser = LensParser(orbParser=OrbParser())

    await parser.orbParser.start_parse()


if __name__ == "__main__":
    asyncio.run(main())
