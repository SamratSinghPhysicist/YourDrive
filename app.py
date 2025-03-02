import asyncio
import functools

# Add back the coroutine decorator that was removed in Python 3.11
if not hasattr(asyncio, 'coroutine'):
    asyncio.coroutine = functools.wraps(lambda f: f)

from mega import Mega

mega = Mega()

mega_accounts = [{ 'email': 'ysuni4@edny.net', 'password': 'Study@123' }, { 'email': 'buv55@edny.net', 'password': 'Study@123' }, { 'email': 'jbk8a@edny.net', 'password': 'Study@123' }, { 'email': 'sezsec@edny.net', 'password': 'Study@123' }, { 'email': 'areklu@edny.net', 'password': 'Study@123' }, { 'email': 'at9q2@edny.net', 'password': 'Study@123' }, { 'email': 'r2nwir@edny.net', 'password': 'Study@123' }, { 'email': 'urac0p@edny.net', 'password': 'Study@123' }, { 'email': 'jaez9h@edny.net', 'password': 'Study@123' }, { 'email': 'm574z@edny.net', 'password': 'Study@123' },]

# m = mega.login("email", "password")

m = mega.login("ysuni4@edny.net", "Study@123")

details = m.get_user()
quota = m.get_quota()

# specify unit output kilo, mega, gig, else bytes will output
space = m.get_storage_space(kilo=True)

files = m.get_files()

print(f"Details: {details}, \n Quota: {quota}, \n Space: {space}")