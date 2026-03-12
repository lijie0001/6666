"""
通讯录 - 命令行入口
使用 telephone 组件实现
"""

from telephone import PhoneBook


def main():
    # 创建通讯录组件，数据保存到 contacts.json
    pb = PhoneBook("contacts.json")

    while True:
        print("\n" + "=" * 30)
        print("  通讯录")
        print("=" * 30)
        print("  1. 添加联系人")
        print("  2. 查找联系人")
        print("  3. 查看全部")
        print("  4. 删除联系人")
        print("  0. 退出")
        print("-" * 30)

        choice = input("请选择: ").strip()

        if choice == "1":
            _add_contact(pb)
        elif choice == "2":
            _search_contact(pb)
        elif choice == "3":
            _list_contacts(pb)
        elif choice == "4":
            _delete_contact(pb)
        elif choice == "0":
            print("再见！")
            break
        else:
            print("✗ 无效选项，请重新选择")


def _add_contact(pb: PhoneBook):
    """添加联系人"""
    name = input("姓名: ").strip()
    phone = input("电话: ").strip()

    if not name:
        print("✗ 姓名不能为空")
        return

    result = pb.add(name, phone)
    if result["ok"]:
        print(f"✓ 添加成功（已格式化为: {result['phone']}）")
    else:
        print(f"✗ {result['error']}")
        print("  - 手机号：11位，如 13800138000")
        print("  - 座机：7-12位数字")


def _search_contact(pb: PhoneBook):
    """查找联系人"""
    keyword = input("输入姓名或电话搜索: ").strip()
    if not keyword:
        print("✗ 请输入搜索内容")
        return
    results = pb.search(keyword)
    if results:
        print("\n找到以下联系人:")
        for c in results:
            print(f"  {c['name']}: {c['phone']}")
    else:
        print("未找到匹配的联系人")


def _list_contacts(pb: PhoneBook):
    """显示所有联系人"""
    contacts = pb.list_all()
    if not contacts:
        print("通讯录为空")
        return
    print("\n所有联系人:")
    print("-" * 30)
    for i, c in enumerate(contacts, 1):
        print(f"  {i}. {c['name']}: {c['phone']}")


def _delete_contact(pb: PhoneBook):
    """删除联系人"""
    contacts = pb.list_all()
    if not contacts:
        print("通讯录为空")
        return
    print("\n所有联系人:")
    print("-" * 30)
    for i, c in enumerate(contacts, 1):
        print(f"  {i}. {c['name']}: {c['phone']}")
    try:
        idx = int(input("\n输入要删除的序号: "))
        result = pb.delete(idx - 1)
        if result["ok"]:
            print(f"✓ 已删除: {result['name']}")
        else:
            print(f"✗ {result['error']}")
    except ValueError:
        print("✗ 请输入有效数字")


if __name__ == "__main__":
    main()
