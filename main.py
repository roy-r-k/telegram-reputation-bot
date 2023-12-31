import pandas as pd
import configfile
import os
import datetime
from datetime import date, datetime
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


'''
To do:

- Make logging database for who has given who reputation when

'''


#Import settings. Set them all in configfile.py
database_path = configfile.database_path
logfile_path = configfile.logfile_path
allowed_chat_id = configfile.allowed_chat_id
admins = configfile.admins
token = configfile.token
bot_username = configfile.bot_username
rank_names = configfile.rank_names
rank_reputation = configfile.rank_reputation

#Check if database exist. If not, make it
if os.path.isfile(database_path) == False:
    pd.DataFrame(columns = ['userid','username','firstname','lastname','rank','reputation','last_recieved_reputation','current_member']).to_csv(database_path, index=False)


#Regular functions
def log(message):
    f = open(logfile_path, 'a', encoding='utf-8')
    f.write('['+str(datetime.now())+'] '+message+'\n')
    f.close
    print('['+str(datetime.now())+'] '+message)

def get_user_value(userid: int, column: str):
    database = pd.read_csv(database_path)
    return database[(database.userid == userid)][column].values[0]

def write_user_value(userid: int, column: str, value):
    database = pd.read_csv(database_path)
    row_index_user = database[(database.userid == userid)].index[0]
    database.at[row_index_user, column] = value
    database.to_csv(database_path, index=False)

#Telegram command functions
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hi! I\'m a bot that keeps track of user reputation and rank in this group'+
                                    '\n\nTo give another user reputation, reply to their message with ''++''\n\n'+
                                    'I also have a few other commands available:\n'+
                                    '<b>!register</b> - Manually register with the bot (Normally not needed)\n'+
                                    '<b>!mystats</b> - Shows your current reputation and rank\n'+
                                    '<b>!stats</b> - Reply to someone with this command to see their reputation and rank\n'+
                                    '<b>!top10</b> - Shows the 10 users with the highest reputation\n'+
                                    '<b>!top25</b> - Shows the 25 users with the highest reputation\n'+
                                    '<b>!bottom10</b> - Shows the 10 users with the lowest reputation\n'+
                                    '\nAdmin only commands:\n'
                                    '<b>!setrep</b> - Set reputation of user manually\n'+
                                    '<b>!norep30days</b> - Show users that have not recieved reputation in last 30 days\n'+
                                    '<b>!norep60days</b> - Show users that have not recieved reputation in last 60 days\n'
                                    , parse_mode='HTML')
    
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    #Information variables of the message
    chat_type: str = update.message.chat.type
    chatid: int = update.message.chat_id
    text: str = update.message.text
    leave = False

    #Store information about original message user and replyer user
    userid = update.message.from_user.id
    username = update.message.from_user.username
    firstname = update.message.from_user.first_name
    lastname = update.message.from_user.last_name

    if update.message.reply_to_message != None:
        message_is_reply = True
        original_message_userid = update.message.reply_to_message.from_user.id
        original_message_firstname = update.message.reply_to_message.from_user.first_name
        original_message_lastname = update.message.reply_to_message.from_user.last_name
    else:
        message_is_reply = False

    #This is a codeblock that runs every time a message is sent in chat
    database = pd.read_csv(database_path)

    if database[(database.userid == userid)].empty:
            #Message from user not yet registered in database, so add them
            log(f'User with ID ({userid}) joined and does not exist yet. Creating..')
            database.loc[len(database.index)] = [userid, username, firstname, lastname, rank_names[0], 0, date.today(), 1]
            
    database.to_csv(database_path, index=False)

    #If lastname is available but not yet in database, fill it in database
    if pd.isnull(get_user_value(userid, 'lastname')) == True and lastname != None:
        write_user_value(userid, 'lastname', firstname)
        log(f'Lastname of user ({userid}) was not yet available in database, but available in telegram. Adding to database...')
    
    #If username is available but not yet in database, fill it in database
    if pd.isnull(get_user_value(userid, 'username')) == True and username != None:
        write_user_value(userid, 'username', username)
        log(f'Username of user ({userid}) was not yet available in database, but available in telegram. Adding to database...')

    #End of codeblock for always on tasks

    #Logging of sent message
    log(f'User {update.message.from_user.first_name} {update.message.from_user.last_name} with ID ({update.message.from_user.id}) and username ({update.message.from_user.username}) in {chat_type} {update.message.chat_id}: "{text}"')

    #Check if bot usage allowed. If not, leave group
    if chatid != allowed_chat_id and allowed_chat_id != False:
        context.bot.send_message(chatid, "This is a private bot. You are not authorised to use this bot. Leaving chat..")
        await app.bot.leave_chat(chatid)
    
    #Make all text lowercase so command is no longer case sensitive
    processed: str = text.lower()

    if "!register" == processed:
        database = pd.read_csv(database_path)

        if database[(database.userid == userid)].empty:
            #New member joined and does not exist yet in database, so add them
            log(f'User with ID ({userid}) used !register command, and I did not know them yet. This is weird. Will add manually now..')
            database.loc[len(database.index)] = [userid, update.message.from_user.username, firstname, lastname, rank_names[0], 0, date.today(), 1]
            database.to_csv(database_path, index=False)
        else:
            #New member joined but already exists in database as left user, only change current_member state
            log(f'User with ID ({userid}) used !register command, and I already knew them.')
              
        await context.bot.send_message(chatid, "Check! You're registered!\n\n<i>For other users reading this: Normally users are automatically registered upon joining the chat. You only need to use this command if you cannot recieve reputation or because staff told you to</i>", parse_mode='HTML')
        return  

    if '++' == processed:
        #Check if message is a reply to a user or a standalone message. If not, return error
        if message_is_reply == False:
            await context.bot.send_message(chatid,"You can only give reputation by replying to a message. Just sending '++' in the chat does not work")
            return

        #Check if original message sender is one of the bots. If so, disallow giving reputation
        if update.message.reply_to_message.from_user.is_bot:
            await context.bot.send_message(chatid,"Thanks, but bots don't need reputation :)")
            return
        
        #Check if person who is giving karma is the same as recieving
        if userid == original_message_userid:
            await context.bot.send_message(chatid,"Giving yourself reputation is forbidden")
            return
        
        #Check if person who is recieving reputation is admin, if so, return simple string and don't affect karma and rank
        if original_message_userid in admins:
            await context.bot.send_message(chatid, f'<b>{firstname} {lastname or ""}</b> gave 1 reputation to <b>{original_message_firstname} {original_message_lastname or ""}</b>!', parse_mode='HTML')
            return
        
        #Error checks passed
        #We are going to add 1 reputation to the user who the message originated from

        #Get current reputation and row index of user
        current_reputation = get_user_value(original_message_userid, 'reputation')

        #Set new reputation and current time
        write_user_value(original_message_userid, 'reputation', (current_reputation + 1))
        write_user_value(original_message_userid, 'last_recieved_reputation', date.today())

        #Update rank if needed
        if current_reputation == rank_reputation[7]:
            write_user_value(original_message_userid, 'rank', rank_names[7])
            rank_upgraded = rank_names[7]
        elif current_reputation == rank_reputation[6]:
            write_user_value(original_message_userid, 'rank', rank_names[6])
            rank_upgraded = rank_names[6]
        elif current_reputation == rank_reputation[5]:
            write_user_value(original_message_userid, 'rank', rank_names[5])
            rank_upgraded = rank_names[5]
        elif current_reputation == rank_reputation[4]:
            write_user_value(original_message_userid, 'rank', rank_names[4])
            rank_upgraded = rank_names[4]
        elif current_reputation == rank_reputation[3]:
            write_user_value(original_message_userid, 'rank', rank_names[3])
            rank_upgraded = rank_names[3] 
        elif current_reputation == rank_reputation[2]:
            write_user_value(original_message_userid, 'rank', rank_names[2])
            rank_upgraded = rank_names[2]
        elif current_reputation == rank_reputation[1]:
            write_user_value(original_message_userid, 'rank', rank_names[1])
            rank_upgraded = rank_names[1]
        else:
            rank_upgraded = False

        #If sender is admin, filter out reputation in reply
        if userid in admins:
            if rank_upgraded == False:
                await context.bot.send_message(chatid, f'<b>{firstname} {lastname or ""}</b> gave 1 reputation to <b>{original_message_firstname} {original_message_lastname or ""}</b> ({int(current_reputation) + 1})!', parse_mode='HTML')
                return
            else:
                await context.bot.send_message(chatid, f'<b>{firstname} {lastname or ""} </b> gave 1 reputation to <b>{original_message_firstname} {original_message_lastname or ""}</b> ({int(current_reputation) + 1})!\n\nCongratulations! Because you reached {int(current_reputation) + 1} reputation, you have reached the rank of {rank_upgraded}!', parse_mode='HTML')
                return
        
        #If rank upgraded, send reputation + upgrade rank message, else only reputation message
        if rank_upgraded == False:
            await context.bot.send_message(chatid, f'<b>{firstname} {lastname or ""}</b> ({get_user_value(userid, "reputation")}) gave 1 reputation to <b>{original_message_firstname} {original_message_lastname or ""}</b> ({int(current_reputation) + 1})!', parse_mode='HTML')
            return
        else:
            await context.bot.send_message(chatid, f'<b>{firstname} {lastname or ""} </b> ({get_user_value(userid, "reputation")}) gave 1 reputation to <b>{original_message_firstname} {original_message_lastname or ""}</b> ({int(current_reputation) + 1})!\n\nCongratulations! Because you reached {int(current_reputation) + 1} reputation, you have reached the rank of {rank_upgraded}!', parse_mode='HTML')
            return

    if '!top25' == processed:

        database = pd.read_csv(database_path)

        #Remove VIP/Staff from selection
        database = database[database['reputation'] < 90000]

        #Filter out non-current members
        database = database[database['current_member'] == 1]
        
        database = database[['userid', 'firstname', 'lastname', 'reputation']].sort_values(by='reputation',ascending=False)

        returnstring = "The top 25 users with the highest reputation are:\n\n"
        count = 1
        
        for row in database.index:
            if pd.isnull(database['lastname'][row]):
                returnstring = returnstring + str(count) + '. '+ str(database['firstname'][row]) +  ' (' + str(database['reputation'][row])+')\n'
            else:
                returnstring = returnstring + str(count) + '. '+ str(database['firstname'][row]) + ' ' + str(database['lastname'][row])+ ' (' + str(database['reputation'][row])+')\n'                
            if count == 25:
                break
           
            count = count + 1

        await context.bot.send_message(chatid, returnstring, parse_mode='HTML')
    
    if '!top10' == processed:
        
        database = pd.read_csv(database_path)

        #Remove VIP/Staff from selection
        database = database[database['reputation'] < 90000]

        #Filter out non-current members
        database = database[database['current_member'] == 1]
        
        database = database[['userid', 'firstname', 'lastname', 'reputation']].sort_values(by='reputation',ascending=False)

        returnstring = "The top 10 users with the highest reputation are:\n\n"
        count = 1
        
        for row in database.index:

            if pd.isnull(database['lastname'][row]):
                returnstring = returnstring + str(count) + '. '+ str(database['firstname'][row]) +  ' (' + str(database['reputation'][row])+')\n'
            else:
                returnstring = returnstring + str(count) + '. '+ str(database['firstname'][row]) + ' ' + str(database['lastname'][row])+ ' (' + str(database['reputation'][row])+')\n'                
            if count == 10:
                break
           
            count = count + 1

        await context.bot.send_message(chatid, returnstring, parse_mode='HTML')
            
    if '!bottom10' == processed:
        
        database = pd.read_csv(database_path)

        #Remove VIP/Staff from selection
        database = database[database['reputation'] < 90000]

        #Filter out non-current members
        database = database[database['current_member'] == 1]

        database = database[['userid', 'firstname', 'lastname', 'reputation']].sort_values(by='reputation',ascending=True)

        returnstring = "The bottom 10 users with the highest reputation are:\n\n"
        count = 1
        
        for row in database.index:
            if pd.isnull(database['lastname'][row]):
                returnstring = returnstring + str(count) + '. '+ str(database['firstname'][row]) +  ' (' + str(database['reputation'][row])+')\n'
            else:
                returnstring = returnstring + str(count) + '. '+ str(database['firstname'][row]) + ' ' + str(database['lastname'][row])+ ' (' + str(database['reputation'][row])+')\n'                
            if count == 10:
                break
           
            count = count + 1

        await context.bot.send_message(chatid, returnstring, parse_mode='HTML')
    
    if '!mystats' == processed:
        #Check if message is a reply to a user or a standalone message. If not, return error
        if message_is_reply == True:
            await context.bot.send_message(chatid, "This command does not work in a reply. Please issue this command in a normal message.")
            return
        
        #Check if user is in admins. If so, return nothing
        if userid in admins:
            await context.bot.send_message(chatid, "The stats of this user are hidden")
            return

        await context.bot.send_message(chatid, 'Your stats are:\n\n'+f'<b>Reputation:</b> {get_user_value(userid, "reputation")}\n<b>Rank:</b> {get_user_value(userid, "rank")}\n<b>Last recieved reputation:</b> {get_user_value(userid, "last_recieved_reputation")}', parse_mode='HTML')
        return
    
    if '!stats' == processed:
        #Check if message is a reply to a user or a standalone message. If not, return error
        if message_is_reply == False:
            await context.bot.send_message(chatid, "You can only get a users stats by replying to their message. Just sending '!getstats' in the chat does not work.")
            return
        
        if update.message.reply_to_message.from_user.is_bot:
            await context.bot.send_message(chatid, "Bots don't have stats :)")
            return
        
        #Check if user is in admins. If so, return nothing
        if userid in admins:
            await context.bot.send_message(chatid, "The stats of this user are hidden")
            return

        await context.bot.send_message(chatid, 'The stats of the user you replied to are:\n\n'+f'<b>Reputation:</b> {get_user_value(original_message_userid, "reputation")}\n<b>Rank:</b> {get_user_value(original_message_userid, "rank")}\n<b>Last recieved reputation:</b> {get_user_value(original_message_userid, "last_recieved_reputation")}', parse_mode='HTML')
        return
    
    if '!setrep' in processed:
        #Setrep command to set reputation of users, so check if user is admin
        if userid not in admins:
            await context.bot.send_message(chatid, "Do not attempt to use commands you are unauthorised to. You will be warned or banned")
            return

        #Check if message is a reply to a user or a standalone message. If not, return error
        if update.message.reply_to_message == None:
            await context.bot.send_message(chatid, "You can only set a users reputation by replying to their message. Just sending '!setrep' in the chat does not work.")
            return
        
        #Check if user gave corrent number of arguments (1). If not, return error
        if len(update.message.text.split()) != 2 | (not update.message.text.split()[1].isdigit()):
            await context.bot.send_message(chatid, "Incorrect arguments for this command. Correct usage: ""!setrep [number]"" as a reply to a user")
            return

        #Check if user is trying to set reputation of bot. If so, return error
        if update.message.reply_to_message.from_user.is_bot:
            await context.bot.send_message(chatid,  "Bots don't have stats :)")
            return
        
        #Checks passed. Execute setrep
        write_user_value(original_message_userid, 'reputation', update.message.text.split()[1])

        #Get current reputation
        current_reputation = get_user_value(original_message_userid, 'reputation')

        #Update rank if needed
        if current_reputation > rank_reputation[7]-1:
            write_user_value(original_message_userid, 'rank', rank_names[7])
            rank_upgraded = rank_names[7]
        elif current_reputation > rank_reputation[6]-1:
            write_user_value(original_message_userid, 'rank', rank_names[6])
            rank_upgraded = rank_names[6]
        elif current_reputation > rank_reputation[5]-1:
            write_user_value(original_message_userid, 'rank', rank_names[5])
            rank_upgraded = rank_names[5]
        elif current_reputation > rank_reputation[4]-1:
            write_user_value(original_message_userid, 'rank', rank_names[4])
            rank_upgraded = rank_names[4]
        elif current_reputation > rank_reputation[3]-1:
            write_user_value(original_message_userid, 'rank', rank_names[3])
            rank_upgraded = rank_names[3] 
        elif current_reputation > rank_reputation[2]-1:
            write_user_value(original_message_userid, 'rank', rank_names[2])
            rank_upgraded = rank_names[2]
        elif current_reputation > rank_reputation[1]-1:
            write_user_value(original_message_userid, 'rank', rank_names[1])
            rank_upgraded = rank_names[1]
        else:
            rank_upgraded = rank_names[0]

        #Send confirmation message in chat
        await context.bot.send_message(chatid, f'Staff set reputation of <b>{original_message_firstname} {original_message_lastname}</b> to {int(current_reputation)}. Rank was automatically updated to {rank_upgraded}', parse_mode='HTML')
        return
    
    if '!norep30days' == processed:
        #Command to check 30 days no karma recieved of users, so check if user is admin
        if userid not in admins:
            await context.bot.send_message(chatid, "Do not attempt to use commands you are unauthorised to. You will be warned or banned")
            return
        
        #Read database and filter database on did not recieve karma in last 30 days and part of non-immune ranks
        database = pd.read_csv(database_path)

        #filter out members with immunity from inactivity
        not_immunitylist = [rank_names[0], rank_names[1], rank_names[2], rank_names[3]]
        database = database[database['rank'].isin(not_immunitylist)]

        #Filter out non-current members
        database = database[database['current_member'] == 1]

        database['last_recieved_reputation'] = pd.to_datetime(database['last_recieved_reputation'], format='%Y-%m-%d')
        database = database[database.last_recieved_reputation < datetime.now() - pd.to_timedelta("30d")]
   

        if database.empty:
            await context.bot.send_message(chatid, "Fantastic! All users have recieved reputation in the last 30 days")
            return

        returnstring = "Users who have not recieved reputation in the last 30 days:\n\n"
        
        for row in database.index:
            returnstring = returnstring + '<b>' +str(database['firstname'][row]) + ' ' + str(database['lastname'][row])+ '</b> (' + str(database['reputation'][row])+') - Last recieved reputation: '+database['last_recieved_reputation'][row].strftime("%Y-%m-%d")+'\n'
            
        await context.bot.send_message(chatid, returnstring, parse_mode='HTML')
        return
    
    if '!norep60days' == processed:
        #Command to check 60 days no reputation recieved of users, so check if user is admin
        if userid not in admins:
            await context.bot.send_message(chatid, "Do not attempt to use commands you are unauthorised to. You will be warned or banned")
            return
        
        #Read database and filter database on did not recieve karma in last 60 days and part of non-immune ranks
        database = pd.read_csv(database_path)

        #filter out members with immunity from inactivity
        not_immunitylist = [rank_names[0], rank_names[1], rank_names[2], rank_names[3]]
        database = database[database['rank'].isin(not_immunitylist)]

        #Filter out non-current members
        database = database[database['current_member'] == 1]

        database['last_recieved_reputation'] = pd.to_datetime(database['last_recieved_reputation'], format='%Y-%m-%d')
        database = database[database.last_recieved_reputation < datetime.now() - pd.to_timedelta("60d")]
   

        if database.empty:
            await context.bot.send_message(chatid, "Fantastic! All users have recieved reputation in the last 30 days")
            return

        returnstring = "Users who have not recieved reputation in the last 60 days:\n\n"
        
        for row in database.index:
            returnstring = returnstring + '<b>' +str(database['firstname'][row]) + ' ' + str(database['lastname'][row])+ '</b> (' + str(database['reputation'][row])+') - Last recieved reputation: '+database['last_recieved_reputation'][row].strftime("%Y-%m-%d")+'\n'
            
        await context.bot.send_message(chatid, returnstring, parse_mode='HTML')
        return

async def handle_newchatmember(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_members = update.message.new_chat_members
    log('New members detected! Printing each one:')
    
    #Open database
    database = pd.read_csv(database_path)

    for new_member in new_members:
        if database[(database.userid == new_member.id)].empty:
            #New member joined and does not exist yet in database, so add them
            log(f'User with ID ({new_member.id}) joined and does not exist yet. Creating..')
            database.loc[len(database.index)] = [new_member.id, new_member.username, new_member.first_name, None, rank_names[0], 0, date.today(), 1]
            database.to_csv(database_path, index=False)

        else:
            #New member joined but already exists in database as left user, only change current_member state
            log(f'User with ID ({new_member.id}) joined and already exists. Changing member state..')
            write_user_value(new_member.id, 'current_member', 1)

    
async def handle_leftchatmember(update: Update, context: ContextTypes.DEFAULT_TYPE):
    left_member = update.message.left_chat_member
    log(str(update))
    log('Left member detected! Handling left member:')
    
    #Open database
    database = pd.read_csv(database_path)

    if database[(database.userid == left_member.id)].empty:
        #Member left, but strangly did not exist yet, so add them with current_member state 0
        log(f'User with ID ({left_member.id}) left and does strangely not exist yet. Creating with current_member state = 0')
        database.loc[len(database.index)] = [left_member.id, left_member.username, left_member.first_name, None, rank_names[0], 0, date.today(), 0]
        database.to_csv(database_path, index=False)
    else:
        #Member left and already exists in database (normal situation). So only change member state
        log(f'User with ID ({left_member.id}) left and exists (normal situation). Changing member state..')
        write_user_value(left_member.id, 'current_member', 0)


async def error (update: Update, context: ContextTypes.DEFAULT_TYPE):
     log(f'Update ({update}) caused error: {context.error}')

if __name__ == '__main__':
    log('Starting....')
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))

    #Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_newchatmember))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, handle_leftchatmember))

    #Errors
    app.add_error_handler(error)

    #polling
    log('Polling....')
    app.run_polling(poll_interval=5)
    
    

