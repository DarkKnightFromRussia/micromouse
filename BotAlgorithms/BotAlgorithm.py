def run(bot):
    while True:
        if bot.colorSensor() == "F":
            break

        if bot.leftDS():
            if bot.frontDS():
                bot.turnRight()
            else:
                bot.driveForward()
        else:
            bot.turnLeft()
            bot.driveForward()
