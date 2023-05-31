import pandas as pd
df_WTA_elo=pd.read_excel(r"C:\Users\chris\OneDrive\Documents\GitHub\tennis_atp\Elo.xlsx",sheet_name="WTA")
df_ATP_elo=pd.read_excel(r"C:\Users\chris\OneDrive\Documents\GitHub\tennis_atp\Elo.xlsx",sheet_name="ATP")

df_ATP_elo=pd.concat([df_ATP_elo,df_WTA_elo])
def GetElo(Player1,Player2,Player1Odds,Player2Odds):
    elo_player1=df_ATP_elo.loc[df_ATP_elo['Player'] == Player1]
    if elo_player1.empty==True:
        elo_player1_overall=0
        elo_player1_clay=0
        elo_player1_hard=0
        elo_player1_rank=0
    else:
        elo_player1_overall=elo_player1["Elo"].values[0]
        elo_player1_clay=elo_player1["gElo"].values[0]
        elo_player1_hard=elo_player1["hElo"].values[0]
        elo_player1_rank=elo_player1["Rank"].values[0]
    elo_player2=df_ATP_elo.loc[df_ATP_elo['Player'] == Player2]
    if elo_player2.empty==True:
        elo_player2_overall=0
        elo_player2_clay=0
        elo_player2_hard=0   
        elo_player2_rank=0 
    else:
        elo_player2_overall=elo_player2["Elo"].values[0]
        elo_player2_clay=elo_player2["gElo"].values[0]
        elo_player2_hard=elo_player2["hElo"].values[0]
        elo_player2_rank=elo_player2["Rank"].values[0]
    Fav=''
    ActualOdds=0
    if elo_player1_overall>elo_player2_overall:
        elo_diff=elo_player1_overall-elo_player2_overall
        elo_diff_clay=elo_player1_clay-elo_player2_clay
        elo_diff_hard=elo_player1_hard-elo_player2_hard
        Fav=Player1
        ActualOdds=Player1Odds
        RankDiff=elo_player1_rank-elo_player2_rank
    else:
        elo_diff=elo_player2_overall-elo_player1_overall
        elo_diff_clay=elo_player2_clay-elo_player1_clay
        elo_diff_hard=elo_player2_hard-elo_player1_hard
        Fav=Player2
        ActualOdds=Player2Odds
        RankDiff=elo_player2_rank-elo_player1_rank
    Prob=0
    Odds=0
    
    Prob= 1-(1 / (1 + (10**((elo_diff) / 400))))
    Prob_clay=1-(1 / (1 + (10**((elo_diff_clay) / 400))))
    Prob_hard=1-(1 / (1 + (10**((elo_diff_hard) / 400))))
    Odds=1/Prob
    Odds_clay=1/Prob_clay
    Odds_hard=1/Prob_hard
    '''  
    if elo_diff >= 500:
        Prob= ">95%"
        Odds=1.05
    elif elo_diff >= 400:
        Prob= ">91%"
        Odds=1.10
    elif elo_diff >= 300:
        Prob= "85%"
        Odds=1.20
    elif elo_diff >= 200:
        Prob=">76%"
        Odds=1.33
    elif elo_diff >= 100:
        Prob=">65%"
        Odds=1.53
    else:
        Prob = "<65%"
        Odds=0
    '''
    return elo_player1_overall, elo_player2_overall,Fav,elo_diff,Prob,Odds,ActualOdds,Odds_clay,Odds_hard,elo_diff_clay,elo_diff_hard,RankDiff

#print(GetElo("Richard Gasquet",'Hugo Dellien')) 
#print(df_ATP_elo[["Player","Elo"]])