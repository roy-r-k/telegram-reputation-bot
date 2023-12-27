#Global variables (settings)
database_path = 'database.csv' #Path to csv file that acts as database
logfile_path = 'log.txt' #Path to text file that acts as logfile
allowed_chat_id = False #Two options: False = Allow all chats, Group ID = Allow operation only in that group
admins = [9999999, 999999] #UserID's that are allowed to use admin commands
token = 'BOT_API_TOKEN' #Bot API token, available via botfather
bot_username = '@bot_username' #Bot username
rank_names = ['Rookie', 'User', 'Member', 'Enthousiast', 'Fanatic', 'Master', 'Legend', 'VIP'] #Rank names
rank_reputation = [0, 50, 150, 300, 500, 750, 1000, 99999] #Amount of reputation needed for every rank