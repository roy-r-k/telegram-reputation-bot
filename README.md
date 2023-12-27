<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->

<!-- ABOUT THE PROJECT -->
## About The Project

I wanted a way to gamify the Telegram group that I'm in. Because there was no bot that did exactly what I wanted, I decided to create it myself. It's 100% written in python and uses the [Python-telegram-bot](https://python-telegram-bot.org/) library/wrapper.

<!-- GETTING STARTED -->
## Features

- Users can give each other reputation points by replying '++' to a message
- When user reaches certain threshold of reputation, bot upgrades user rank
- Bot keeps track of reputation and rank of user
- Authorised users (by userid in config) can set reputation and thereby rank manually

<!-- RUNNING THIS BOT -->
## Running your own bot

1. Get an account at PythonAnywhere.com
2. Clone the repo
   ```sh
   
   git clone https://github.com/roy-r-k/telegram-reputation-bot
   
   ```
3. Upload all files to PythonAnywhere
4. Create bot in BotFather and save API key and bot username.
5. Add bot to your chat, and make it admin
6. Enter desired settings, API key (step 4) and bot username (step 4) in configfile.py
7. Run main.py
8. Test if bot is working by typing a chat message. The message should show up in log.txt



<!-- ROADMAP -->
## Roadmap

- [ ] Keep staff out of '++', !getrep, !norep30days and !norep60days
- [ ] Check if log.txt and database.csv exists. If not, make them automatically
- [ ] Make logging database for who has given who reputation when

See the [open issues](https://github.com/roy-r-k/telegram-reputation-bot/issues) for a full list of proposed features (and known issues).



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.


<!-- CONTACT -->
## Contact

You can contact me by comment on GitHub

Project Link: [https://github.com/roy-r-k/telegram-reputation-bot/
](https://github.com/roy-r-k/telegram-reputation-bot/)


<!-- ACKNOWLEDGMENTS -->
## Inspired by

- [Niscoin XP Telegram bot](https://github.com/Nischay-Pro/niscoin)

<p align="center">(<a href="#readme-top">back to top</a>)</p>
