function sendMessage(bot, playerName, message) { 
    bot.chat(`@${playerName} ${message}`)
}

export { sendMessage }