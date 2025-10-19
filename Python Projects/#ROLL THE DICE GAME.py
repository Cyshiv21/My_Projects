#ROLL THE DICE GAME
import random
while True:
    choice = input("Roll the Dice(y/n): ").strip().lower()
    if choice == 'y':
        finite_set = (1 , 2, 3, 4, 5, 6)
        num1 = random.choice(finite_set)
        num2 = random.choice(finite_set)
        print(f'({num1}, {num2})')

    elif choice == 'n':
        print("Thank You For Playing!! :)")
        break
    else:
        print("invalid choice! please try again.")


