def get_wallet():
    with open("results/eligible123.txt", "r") as file:

        content = file.readlines()

        for line in content:
            splitted = line.split("|")

            if not splitted[2].strip().startswith("0x"):
                pass

            wallet = splitted[2].strip()

            print(wallet)


if __name__ == "__main__":
    get_wallet()