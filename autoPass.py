import streamlit as st




def autoPass(rank, pct_played, final_teams):


        if rank <=10:
            rankTarget = .30
            if pct_played >= rankTarget:
                return([ 1, f"AUTO-PASS GRANTED: The player has played {int(pct_played * 100)}% of competitive matches in the last 24 months for a team ranked between 1-10 [ {rank} ]"])
            elif pct_played >= .20:
                return([ 2, f"AUTO-PASS NEAR-MISS: The player has played {int(pct_played * 100)}% of competitive matches in the last 24 months, this is just below the {rankTarget*100}% threshold for a team ranked between 1-10 [ {rank} ] but they are close to meeting the auto-pass threshold"])
            else:
                return([ 0, f"AUTO-PASS FAIL: The player has only played {int(pct_played * 100)}% of competitive matches in the last 24 months, this is not above the {rankTarget*100}%  threshold for a team ranked between 1-10 [ {rank} ]"])
        
        elif rank <=20:
            rankTarget = .40
            if pct_played >= rankTarget:
                return([ 1, f"AUTO-PASS GRANTED: The player has played {int(pct_played * 100)}% of competitive matches in the last 24 months for a team ranked between 11-20 [ {rank} ]"])
            elif pct_played >= .20:
                return([ 2, f"AUTO-PASS NEAR-MISS: The player has played {int(pct_played * 100)}% of competitive matches in the last 24 months, this is just below the {rankTarget*100}% threshold for a team ranked between 11-20 [ {rank} ] but they are close to meeting the auto-pass threshold"])
            else:
                return([ 0, f"AUTO-PASS FAIL: The player has only played {int(pct_played * 100)}% of competitive matches in the last 24 months, this is not above the {rankTarget*100}%  threshold for a team ranked between 11-20 [ {rank} ]"])
        
        elif rank <=30:
            rankTarget = .60
            if pct_played >= rankTarget:
                return([ 1, f"AUTO-PASS GRANTED: The player has played {int(pct_played * 100)}% of competitive matches in the last 24 months for a team ranked between 21–30 [ {rank} ]"])
            elif pct_played >= .20:
                return([ 2, f"AUTO-PASS NEAR-MISS: The player has played {int(pct_played * 100)}% of competitive matches in the last 24 months, this is just below the {rankTarget*100}% threshold for a team ranked between 21–30 [ {rank} ] but they are close to meeting the auto-pass threshold"])
            else:
                return([ 0, f"AUTO-PASS FAIL: The player has only played {int(pct_played * 100)}% of competitive matches in the last 24 months, this is not above the {rankTarget*100}%  threshold for a team ranked between 21–30 [ {rank} ]"])
        
        elif rank <=50:
            rankTarget = .70
            if pct_played >= rankTarget:
                return([ 1, f"AUTO-PASS GRANTED: The player has played {int(pct_played * 100)}% of competitive matches in the last 24 months for a team ranked between 31–50 [ {rank} ]"])
            elif pct_played >= .20:
                return([ 2, f"AUTO-PASS NEAR-MISS: The player has played {int(pct_played * 100)}% of competitive matches in the last 24 months, this is just below the {rankTarget*100}% threshold for a team ranked between 31–50 [ {rank} ] but they are close to meeting the auto-pass threshold"])
            else:
                return([ 0, f"AUTO-PASS FAIL: The player has only played {int(pct_played * 100)}% of competitive matches in the last 24 months, this is not above the {rankTarget*100}%  threshold for a team ranked between 31–50 [ {rank} ]"])

        
        elif rank >50:
            return([ 0, f"AUTO-PASS FAIL: {final_teams[0]}'s FIFA Raking [{rank}] is below the auto-pass threshold of 50. Therefore the auto-pass criteria has not been met"])

        else:
            return([ 4, f"RANK UNDER CONSTRUCTION"])