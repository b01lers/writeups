# Trend Micro : You Gotta Know When to Fold 'em, Know when to hold 'em

#### Author: scott1024

**Description**:
> I'm playing heads up blackjack.  I'm dealt Ace-2 and the dealer has 3 showing.  What's the probably of winning if: 1) I stand or 2) I kept playing.

I'm not limited to just hitting once.  In fact, after each card I apply the decision criteria: if my probably of winning when I continue is greater than the probability of winning if I stand, I continue, otherwise I stand.  The probablity of winning at state N depends on the probability of winning at N+1, N+2, N+3, ... until I bust or stand.  The probability of winning if I continue is recursive in some sense.

While my strategy is dynamic, the dealer's strategy is static.  He stands anytime he gets 17 or higher.  He hits whenever he has 16 or less.

We play with two regular decks giving us 104 cards in total.

# The Solution

![Monte Carlo All the Things!](http://i.imgur.com/waepRcZ.jpg)

I took a statistics class last summer and I learned many formulas and techniques, but the biggest lesson I learned is that if I can simulate something I can use [Monte Carlo](https://en.wikipedia.org/wiki/Monte_Carlo_method) to approximate the distribution.  Monte Carlo is amazing for programmers because we're generally good at programming but not so good at manipulating probability equations.

The problem is that for a given hand my decision procedure depends on already knowing two probabilities: 1) the probability of the dealer beating me if I stop now 2) the probability of winning if I continue.  But 2) is the very probability I'm trying to approximate using Monte Carlo.  I won't know the true probability until I've run many simulations so I can't use this decision procedure exactly.  I need to approximate it.

The probability of winning if I stand at any given point is relatively easy to calculate using Monte Carlo.  I need to simulate the dealer playing many times, but first I will show how to run a single iteration.  Further, technially the dealer simulation should depend on what cards I drew because that changes the probabilities of his card draws.  If I draw a 3 as my first card, that changes all the subsequent card draw probabilites.  To truly model the dealer outcomes I would need to have a different probability distribution for every on of my possible hands.  Now I'm having to run Monte Carlo simulations inside my Monte Carlo simulations.  This would take too long.

I made two key assumptions:

1) I could approximate the probability of the dealer beating me when I have a particular hand by calculating the probability of the dealer getting each possible score (17, 18, 19, 20, 21, or bust) given that I stand with my starting hand.  This gives me one static dealer score probability distribution that I only ever need to calculate once, but will be slightly off because it doesn't take into account the cards I might have drawn.
2) I guessed that my optimal strategy would be very close to the "by-the-book" strategy used by real-world blackjack players.  You can find action tables for blackjack online that you can use to look up what you should do given your current hand and the dealer's face up card.

![an example blackjack strategy card](http://www.cardcountingtrainer.com/wp-content/uploads/2013/01/FinalBBSchart.png)

# The Code

The function *get_dealer_decision* applies the dealer's decision procedure given his current hand.


    def get_dealer_decision(dealer_hand):
        # return the final score if the dealer stops
        # or -2 if he should hit
        # or -1 is he busted
        totals, hands = total_hand(dealer_hand)
        useable_hands = filter(is_not_busted, totals)
        if len(useable_hands) == 0:
            return BUSTED
        best = max(useable_hands)
        if best >= 17:
            return best
        return HIT


The function *simulate_dealer_once* sets up the deck and then calls *simulate_dealer_hand* which is where the hand is actually played.


    def simulate_dealer_once():
        deck = Deck()
        deck.remove(dealer_face_up_card)
        deck.remove('A')
        deck.remove('2')
        score, hand = simulate_dealer_hand(deck)
        return score # decision is his final score or -1 for busted


To play the hand the dealer evaluates his decision procedure then acts accordingly.


    def simulate_dealer_hand(deck):
        dealer_hand = [dealer_face_up_card]
        while True:
            dealer_hand.append(deck.deal())
            decision = get_dealer_decision(dealer_hand)
            if decision != HIT:
                break
        return decision, dealer_hand


So *simulate_dealer_once* simulates the dealer playing his hand to completion given the starting deck. Now all I have to do is simulate the dealer playing over and over.


    def simulate_dealer():
        dealer_sim_results = [0]*N_DEALER_SIMS
        for i in range(N_DEALER_SIMS):
            dealer_sim_results[i] = simulate_dealer_once()
        return dealer_sim_results


Now I don't want to re-run this simulate everytime, so I use numpy to save the data.  Note that I keep the results in an array where the *i*-th index holds the probability of the dealer getting the score *i*.


    def save_numpy_file(sim_res):
        dealer_probs = np.zeros((22,1), dtype=float)
        for score in POSSIBLE_DEALER_RESULTS:
            tmp = sim_res.count(score)
            tot = len(sim_res)
            if score != -1:
                dealer_probs[score] = float(tmp) / float(tot)
            else:
                dealer_probs[0] = float(tmp) / float(tot)
        np.save(fname, dealer_probs)


On to simulating playing my hand.  The code to simulate my play is essentially the same as the dealer except I use a different decision procedure.

My criteria to hit or stand is a boolean variable calculated by:


    while (stand_win_total <= 11 and stand_win_prob < .5) \
                or (stand_win_total < 17 and has_soft_ace(stand_win_hand)):


Here *stand_win_total* is my current score, *stand_win_prob* is calculated by summing the probability that the dealer scores less than my current total or busts and *has_soft_ace* is a function that returns true if in my current hand I'm using an Ace as 11 (a soft ace).  I can never bust if I hit with a soft ace, so it's better strategy to hit if I don't have a good hand.  Note that this isn't exactly the "by-the-book" procedure, but I'm pretty use it effective is the same.  That is:


    while stand_win_total <= 11) \
            or (stand_win_total < 17 and has_soft_ace(stand_win_hand)):


Now I can play simulate my "real" strategy by using this "by-the-book" strategy and my dealer score distribution I calculated earlier.  Then I can do Monte Carlo.  I just simulate tons and tons of hands and eventually the probability of winning that I'm calculating based on my simulation converges to the real probablity.

# The Answer

This simulation gives me the probability of winning if I continue.  What is the probability of winning if I stand?  Well, I already calculated that in my dealer simulation.  It's just the probability that the dealer doesn't bust if I stand with my starting hand. He will never stop at less than my starting score (13).

The probability of winning if I continue is 0.5094.
The probability of winning if I stand is 0.3770.

This make intuitive sense because I have a soft Ace and a low total (13).  Good strategy is to hit in an attempt to improve my score since I cannot bust.

The complete code is [here.](https://github.com/scottcarr/ctf/blob/master/TrendMicroCtfAsiaPacific2015/blackjack.py)
 
