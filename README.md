# Investopedia API Wrapper
 Manage your Investopedia account with this api wrapper.

You need to install ==selenium== to run this.

My finance class is having a stock trading competition on investopedia so I decided to make a bot trade for me.

I will be constantly updating and maintaining this for the next couple of months.

# Example Code
```
import Investopedia
client = Investopedia.Account("username", 'password')
client.change_game_session("Investopedia Trading Game")
print(client.get_account_overview())
client.trade("dell", Investopedia.Action.buy, 4)
client.trade("dell", Investopedia.Action.sell, 3)
```