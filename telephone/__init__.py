"""
telephone - 通讯录组件
可复用的联系人管理模块，支持电话格式验证
"""

from .phone_book import PhoneBook, validate_phone

__all__ = ["PhoneBook", "validate_phone"]
