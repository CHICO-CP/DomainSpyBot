
# DomainSpyBot 🖥️

Welcome to **DomainSpyBot**! 🚀 This Telegram bot is designed to perform advanced searches for associated domains, port scans, IP lookups, and much more. It's the perfect tool for cybersecurity enthusiasts and users who want to explore related domains effortlessly.

## Main Features ✨

- **Reverse IP Lookup**: Find domains associated with an IP or domain.
- **Port Scanning**: Detect open ports on any domain.
- **IP Lookup**: Quickly get the IP address of a domain.
- **History and Downloads**: Save your searches and download the results.
- **Supported Languages**: Spanish and English.

## Available Commands 📚

- `/start` - Display the welcome message.
- `/setlang [es|en]` - Change the bot's language.
- `/history` - View your search history.
- `/stats` - Show bot usage statistics.
- `/port [domain]` - Scan open ports.
- `/ip [domain]` - Get the IP address of a domain.

## Installation and Setup ⚙️

1. Clone this repository:  
   ```bash
   git clone https://github.com/CHICO-CP/DomainSpyBot.git
   ```

2. Install the necessary dependencies:  
   ```bash
   pip install -r requirements.txt
   ```
   
   ```bash
   pkg install nmap
   ```

3. Set up your bot token in the .env file (`your_token_bot`).

4. Run the bot:  
   ```bash
   python run.py
   ```

## Example of Use 🚀

Send a message to the bot with an IP address (e.g., `8.8.8.8`) or a domain (e.g., `google.com`) to get the associated domains.

## Credits 👨‍💻

- **Developer**: `@Gh0stDeveloper`
- **GitHub**: [CHICO-CP](https://github.com/CHICO-CP)

We hope you find DomainSpyBot useful! Feel free to contribute or report issues in the repository.
