def sort_balance():
    with open("../results/balances.txt", "r") as balances:
        lines = balances.readlines()

        for line in lines:
            addr, balance = line.split(":")
            print(addr, balance)

            if 0 <= float(balance.strip()) <= 100:
                file_path = "../results/balances/0_100.txt"
            elif 101 <= float(balance.strip()) <= 500:
                file_path = "../results/balances/101_500.txt"
            elif 501 <= float(balance.strip()) <= 1000:
                file_path = "../results/balances/501_1000.txt"
            else:
                file_path = "../results/balances/1001_plus.txt"

            with open(file_path, "a") as b_output:
                b_output.write(f"{addr}\n")

if __name__ == "__main__":
    sort_balance()