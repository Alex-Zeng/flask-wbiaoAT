from ext import db

# 操作设备配置管理
class EquipmentManagement(db.Model):
    __tablename__ = 'equipment_management'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, comment="配置名")
    platformName = db.Column(db.String(100), nullable=False, comment="使用的手机操作系统")
    platformVersion = db.Column(db.String(100), nullable=False, comment="手机操作系统的版本")
    deviceName = db.Column(db.String(100), nullable=False, comment="使用的手机或模拟器类型")
    appPackage = db.Column(db.String(100), nullable=False, comment="包名")
    appActivity = db.Column(db.String(100), nullable=False, comment="启动页")
    automationName = db.Column(db.String(100), nullable=False, comment="automationName")
    noReset = db.Column(db.String(100), nullable=False, comment="在当前 session 下不会重置应用的状态。")
    dontStopAppOnRest = db.Column(db.String(100), nullable=False, comment="(仅安卓) 用于设置appium重启时是否先杀掉app")
    autoGrantPermissions = db.Column(db.String(100), nullable=False, comment="自动确定您的应用需要哪些权限")
    systemPort = db.Column(db.Integer, nullable=False, comment="并发执行时需要用到")
    remoteHost = db.Column(db.String(100), nullable=False, comment="远程appium服务器地址")
    remotePort = db.Column(db.Integer, nullable=False, comment="远程appium服务器端口")