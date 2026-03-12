"""
猜数字游戏
电脑随机想一个 1-100 的数字，你来猜！
"""

import random


def main():
    # 1. 电脑随机生成 1-100 的数字
    secret = random.randint(1, 100)
    guess_count = 0

    print("=" * 40)
    print("  猜数字游戏：我想了一个 1-100 的数字")
    print("=" * 40)

    while True:
        # 2. 获取用户输入
        try:
            guess = int(input("\n请输入你的猜测: "))
        except ValueError:
            print("请输入有效的数字！")
            continue

        guess_count += 1

        # 3. 比较并给出提示
        if guess < secret:
            print("太小了，再大一点！")
        elif guess > secret:
            print("太大了，再小一点！")
        else:
            print(f"\n🎉 猜对了！答案是 {secret}")
            print(f"你一共猜了 {guess_count} 次")
            break


if __name__ == "__main__":
    main()
