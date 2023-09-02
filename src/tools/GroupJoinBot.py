import requests
from Tool import Tool
import concurrent.futures
from CaptchaSolver import CaptchaSolver

class GroupJoinBot(Tool):
    def __init__(self, app):
        super().__init__("Group Join Bot", "Enhance the size of your group members", 7, app)

        self.max_generations = self.config["max_generations"]
        self.captcha_solver = self.config["captcha_solver"]
        self.max_workers = self.config["max_workers"]
        self.use_proxy = self.config["use_proxy"]

        self.cookies_file_path = self.app.cookies_file_path

    def run(self):
        group_id = input("Group ID to increase members count: ")

        cookies = self.get_cookies(self.max_generations)

        req_worked = 0
        req_failed = 0
        total_req = len(cookies)

        print("Please wait... \n")

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = [executor.submit(self.send_group_join_request, self.captcha_solver, group_id, cookie) for cookie in cookies]

            for future in concurrent.futures.as_completed(results):
                has_joined, response_text = future.result()

                if has_joined:
                    req_worked += 1
                else:
                    req_failed += 1
                print("\033[1A\033[K\033[1A\033[K\033[1;32mNew joins: "+str(req_worked)+"\033[0;0m | \033[1;31mFailed: "+str(req_failed)+"\033[0;0m | \033[1;34mTotal: "+str(total_req) + "\033[0;0m")
                print("\033[1;32mWorked: " + response_text + "\033[0;0m" if has_joined else "\033[1;31mFailed: " + response_text + "\033[0;0m")

    
    def send_group_join_request(self, captcha_service:str, group_id:str | int, cookie:str):
        err = None
        for _ in range(3):
            try:
                captcha_solver = CaptchaSolver(captcha_service, self.captcha_tokens[captcha_service])
                proxies = self.get_random_proxies() if self.use_proxy else None
                user_agent = self.get_random_user_agent()
                csrf_token = self.get_csrf_token(proxies, cookie)

                req_url = f"https://groups.roblox.com/v1/groups/{group_id}/users"
                req_cookies = {".ROBLOSECURITY": cookie}
                req_headers = {"User-Agent": user_agent, "Accept": "application/json, text/plain, */*", "Accept-Language": "en-US;q=0.5,en;q=0.3", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/json;charset=utf-8", "X-Csrf-Token": csrf_token, "Origin": "https://www.roblox.com", "Referer": "https://www.roblox.com/", "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-site", "Te": "trailers"}
                req_json={"redemptionToken": "", "sessionId": ""}

                init_res = requests.post(req_url, headers=req_headers, cookies=req_cookies, json=req_json, proxies=proxies)
                response = captcha_solver.solve_captcha(init_res, "ACTION_TYPE_GROUP_JOIN", user_agent, csrf_token, proxies)
                break
            except Exception as e:
                err = str(e)
        else:
            return False, err
        
        return (response.status_code == 200), response.text