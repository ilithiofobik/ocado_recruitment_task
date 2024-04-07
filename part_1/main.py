import csv
import sys
from os import path
from pulp import *

def output_name(input_name):
    dir = path.dirname(input_name)
    file_name = path.basename("output.csv")

    return path.join(dir, file_name)

def add_debt(debts, debtor, creditor, amount):
    if debtor not in debts:
        debts[debtor] = 0 
    if creditor not in debts:
        debts[creditor] = 0
    
    debts[debtor] += amount
    debts[creditor] -= amount

def calc_debts(input_file):
    debts = { }

    with open(input_file, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            creditor = row[0]
            debtor = row[1]
            amount = int(row[2])
            add_debt(debts, debtor, creditor, amount)

    return debts

def optimize_transactions(debts):
    repays = []
    
    debtors = [ (amount, person) for person, amount in debts.items() if amount > 0 ]
    creditors = [ (-amount, person) for person, amount in debts.items() if amount < 0 ]

    max_amount = max([amount for amount, _ in debtors] + [-amount for amount, _ in creditors])

    # Creating the problem
    prob = LpProblem("DebtRepayment", LpMinimize)

    is_paying = {} 
    pay_amount = {}

    # Creating variables representing payments
    for d_amount, debtor in debtors:
        for _, creditor in creditors:
            lp_is_paying = LpVariable(f"{debtor}_pays_{creditor}", cat=LpBinary)
            lp_amount = LpVariable(f"{debtor}_amount_{creditor}", lowBound=0, upBound=d_amount)

            is_paying[(debtor, creditor)] = lp_is_paying
            pay_amount[(debtor, creditor)] = lp_amount

    #Creating the constrains on sums of payments
    for amount, creditor in creditors:
       prob += lpSum([pay_amount[(debtor, creditor)] for _, debtor in debtors]) == amount

    for amount, debtor in debtors:
       prob += lpSum([pay_amount[(debtor, creditor)] for _, creditor in creditors]) == amount

    # If a debtor pays a creditor, the amount must be greater than 0
    for _, debtor in debtors:
        for _, creditor in creditors:
            prob += pay_amount[(debtor, creditor)] <= is_paying[(debtor, creditor)] * max_amount

    # Minimum number of transactions
    prob.objective = lpSum([is_paying[(debtor, creditor)] for _, debtor in debtors for _, creditor in creditors])

    # Solve the problem
    prob.solve(PULP_CBC_CMD(msg=0))

    # Print the results
    for _, debtor in debtors:
        for _, creditor in creditors:
            if is_paying[(debtor, creditor)].value() == 1:
                amount = int(pay_amount[(debtor, creditor)].value())
                repays.append((debtor, creditor, amount))

    return repays

def save_repays(repays, output_file):
    with open(output_file, "w+", newline='') as f:
        writer = csv.writer(f)
        for debtor, creditor, amount in repays:
            writer.writerow([debtor, creditor, amount])


if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = output_name(input_file)

    # print output file
    print(output_file)

    debts = calc_debts(input_file)
    repays = optimize_transactions(debts)
 
    save_repays(repays, output_file)