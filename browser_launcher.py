import webbrowser


def launch_browser(url="https://www.google.com"):
    """
    Tries preferred browsers first, then falls back to system default.
    """
    browser_preferences = ['google-chrome', 'chrome', 'firefox', 'opera']

    for browser_name in browser_preferences:
        try:
            browser = webbrowser.get(browser_name)
            browser.open(url)
            print(f"[+] Browser launched using: {browser_name}")
            return
        except webbrowser.Error:
            continue

    webbrowser.open(url)
    print("[+] Browser launched using system default")
