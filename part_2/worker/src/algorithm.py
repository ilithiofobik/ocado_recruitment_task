import csv
from pulp import *

# Adding debt to the debts dictionary
# If the debtor or creditor is not in the dictionary, add them with 0 debt
def add_debt(debts, debtor, creditor, amount):
    if debtor not in debts:
        debts[debtor] = 0 
    if creditor not in debts:
        debts[creditor] = 0
    
    debts[debtor] += amount
    debts[creditor] -= amount

# Sum up the debts from the input file
def calc_debts(f):
    debts = { }

    reader = csv.reader(f)
    for row in reader:
        creditor = row[0]
        debtor = row[1]
        amount = int(row[2])
        add_debt(debts, debtor, creditor, amount)

    return debts

# Optimize the transactions using mixed integer programming
def optimize_transactions(debts):
    # List of final repayements
    repays = []
    
    # Splitting all actors into debtors and creditors
    debtors = [ (amount, person) for person, amount in debts.items() if amount > 0 ]
    creditors = [ (-amount, person) for person, amount in debts.items() if amount < 0 ]

    # Creating the problem
    prob = LpProblem("DebtRepayment", LpMinimize)

    # This variable defines whether debtor x pays creditor y
    is_paying = {} 
    # This variable defines how much debtor x pays creditor y
    pay_amount = {}

    # Creating variables representing payments
    for d_amount, debtor in debtors:
        for _, creditor in creditors:
            lp_is_paying = LpVariable(f"{debtor}_pays_{creditor}", cat=LpBinary)
            lp_amount = LpVariable(f"{debtor}_amount_{creditor}", lowBound=0, upBound=d_amount)

            is_paying[(debtor, creditor)] = lp_is_paying
            pay_amount[(debtor, creditor)] = lp_amount

    # Every creditor should receive the amount he is owed
    for amount, creditor in creditors:
        prob += lpSum([pay_amount[(debtor, creditor)] for _, debtor in debtors]) == amount

    # Every debtor should pay the amount he owes
    for amount, debtor in debtors:
        prob += lpSum([pay_amount[(debtor, creditor)] for _, creditor in creditors]) == amount

    # If a debtor pays a creditor, the amount must be greater than 0
    for d_amount, debtor in debtors:
        for _, creditor in creditors:
            # Debtor pays maximum the amount he owes
            # If the debtor is not paying, the amount must be 0
            prob += pay_amount[(debtor, creditor)] <= is_paying[(debtor, creditor)] * d_amount

    # Minimum number of transactions
    prob.objective = lpSum([is_paying[(debtor, creditor)] for _, debtor in debtors for _, creditor in creditors])

    # Solve the problem using a branch and cut solver
    prob.solve(PULP_CBC_CMD(msg=0))

    # Save the results
    for _, debtor in debtors:
        for _, creditor in creditors:
            if is_paying[(debtor, creditor)].value() == 1:
                amount = int(pay_amount[(debtor, creditor)].value())
                repays.append((debtor, creditor, amount))

    return repays