from ext import db

# 操作设备配置管理
class EquipmentManagement(db.Model):
    __tablename__ = 'equipment_management'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, comment="配置名")
    setting_args = db.Column(db.Text, comment="配置参数")
    status = db.Column(db.Integer,default=0, nullable=False, comment="运行状态 0停止,1运行中")
    session_id = db.Column(db.String(100), nullable=True, comment="session_id")
    remoteHost = db.Column(db.String(100), nullable=False, comment="远程appium服务器地址")
    remotePort = db.Column(db.Integer, nullable=False, comment="远程appium服务器端口")

    test_case_suit = db.relationship('EquipmentIncludeTesSuit', backref=db.backref('equipment'), order_by='EquipmentIncludeTesSuit.rank')

# 使用设备执行的一些用例集
class EquipmentIncludeTesSuit(db.Model):
    __tablename__ = 'equipment_include_test_suit'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    equipment_id = db.Column(db.Integer,db.ForeignKey('equipment_management.id'), nullable=False, comment="设备ID")
    test_case_suit_id = db.Column(db.Integer, db.ForeignKey('test_case_suit.id'),comment="测试集ID")
    rank = db.Column(db.Integer, nullable=False, comment="执行顺序")
    update_datetime = db.Column(db.DateTime, nullable=False,
                                server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间")

    test_case_suit = db.relationship('TestCaseSuit')
