# sAuction

> Smart Auctions Portal Flowchart

```mermaid
graph TB
    U1((user 1))
    U2((user 2))
    U3((user 3))
    U4((user 4))
    U1 & U2 & U3 & U4 --> C
    
    subgraph main
      A[Auction Dashboard]
      B((Admin Portal))
      C[Bidding Portal]
    end
    subgraph backend
      D(Data Broker/Storage)
      E((Redis))
    end
    
    A & B & C <--> D
```

## GUIDE To Use (sAuctions)

- Bidding Portal - https://biddings.streamlit.app/

Step 1 : Enter your login code to get access to your Teams Bidding Portal
Step 2 : Enter your Bid & start Bidding!

- Auction Dashboard Portal - https://sauction.streamlit.app/

> File format

- dashboard.py - auction status & live dashboard
  - pages/admin.py - admin settings panel
- bidding.py - team portal for bidding - seperate [repo](https://github.com/hirawatt/bidding)

> Data required

- 

> Glossary

- lb - last bid
- 