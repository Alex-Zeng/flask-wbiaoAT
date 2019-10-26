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



# 执行用例参数表
class TestArgs(db.Model):
    __tablename__ = 'test_args'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cycle_time = db.Column(db.Integer, nullable=False,comment="第几次循环")
    key = db.Column(db.String(100), nullable=False, comment="参数名")
    value = db.Column(db.Text, comment="参数值")
    create_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"), comment="创建时间")
    update_datetime = db.Column(db.DateTime, nullable=False,
                                server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间")
