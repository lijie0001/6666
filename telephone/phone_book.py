"""
telephone 组件 - 通讯录核心逻辑
提供 PhoneBook 类，可在其他项目中导入使用
"""

import json
import os
import re


def validate_phone(phone: str) -> tuple[bool, str | None]:
    """
    验证电话格式
    - 手机号：11位，1开头
    - 座机：7-12位数字
    返回：(是否有效, 格式化后的号码)
    """
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)
    if cleaned.startswith("+86"):
        cleaned = cleaned[3:]
    elif cleaned.startswith("86") and len(cleaned) > 10:
        cleaned = cleaned[2:]

    if not cleaned.isdigit():
        return False, None

    if len(cleaned) == 11 and cleaned.startswith("1"):
        return True, cleaned
    if 7 <= len(cleaned) <= 12:
        return True, cleaned

    return False, None


class PhoneBook:
    """通讯录组件 - 可在任何项目中导入使用"""

    def __init__(self, data_file: str = "contacts.json"):
        self.data_file = data_file
        self._contacts: list[dict] = []
        self.load()

    def load(self) -> list[dict]:
        """从文件加载联系人"""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                self._contacts = json.load(f)
        else:
            self._contacts = []
        return self._contacts

    def save(self) -> None:
        """保存到文件"""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self._contacts, f, ensure_ascii=False, indent=2)

    def add(self, name: str, phone: str) -> tuple[bool, str]:
        """
        添加联系人
        返回：(是否成功, 提示信息)
        """
        if not name.strip():
            return False, "姓名不能为空"
        if not phone.strip():
            return False, "电话不能为空"

        valid, formatted = validate_phone(phone)
        if not valid:
            return False, "电话格式无效，手机号11位或座机7-12位"

        self._contacts.append({"name": name.strip(), "phone": formatted})
        self.save()
        return True, f"添加成功（已格式化为: {formatted}）"

    def search(self, keyword: str) -> list[dict]:
        """按姓名或电话搜索"""
        keyword = keyword.strip()
        if not keyword:
            return []
        return [
            c for c in self._contacts
            if keyword in c["name"] or keyword in c["phone"]
        ]

    def list_all(self) -> list[dict]:
        """返回所有联系人"""
        return self._contacts.copy()

    def delete(self, index: int) -> tuple[bool, str]:
        """
        按序号删除（从1开始）
        返回：(是否成功, 提示信息)
        """
        if index < 1 or index > len(self._contacts):
            return False, "序号无效"
        removed = self._contacts.pop(index - 1)
        self.save()
        return True, f"已删除: {removed['name']}"
