from ext import db

# 操作设备配置管理
class EquipmentManagement(db.Model):
    __tablename__ = 'equipment_management'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, comment="配置名")
    setting_args = db.Column(db.Text, comment="配置参数")
    status = db.Column(db.Integer,default=0, nullable=False, comment="运行状态 0停止,1运行中")
    cron_status = db.Column(db.Integer,default=0, nullable=False, comment="定时任务状态 0停止,1启动")
    cron_times = db.Column(db.String(100), nullable=True, comment="crontab表达式")
    next_run_time = db.Column(db.String(100), nullable=True, comment="下次任务运行时间")
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

class TestLog(db.Model):
    __tablename__ = 'test_log'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    equipment_id = db.Column(db.Integer, nullable=False, comment="设备ID")
    equipment_title = db.Column(db.String(100), nullable=False, comment="设备")
    equipment_args = db.Column(db.Text, comment="设备配置参数")
    run_test_result = db.Column(db.Integer, default=0, comment="测试执行结果:0失败,1成功")

    run_test_start_time = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"), comment="测试执行开始时间")
    run_test_end_time = db.Column(db.DateTime, nullable=False,server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="测试执行结束时间")
    run_test_times = db.Column(db.String(100), default=0, comment="测试执行用时时间")

    test_case_suit_log = db.relationship('TestCaseSuitLog',order_by='TestCaseSuitLog.run_test_suit_start_time')

class TestCaseSuitLog(db.Model):
    __tablename__ = 'test_case_suit_log'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    test_log_id = db.Column(db.Integer, db.ForeignKey('test_log.id'), comment="所属测试日志ID")
    test_case_suit_id = db.Column(db.Integer, db.ForeignKey('test_case_suit.id'), comment="测试集ID")
    test_case_suit_title = db.Column(db.String(100), nullable=False, comment="测试集标题")
    run_test_result = db.Column(db.Integer, nullable=False, comment="测试执行结果:0失败,1成功")
    run_test_suit_start_time = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"), comment="测试集执行开始时间")
    run_test_suit_end_time = db.Column(db.DateTime, nullable=False,server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="测试集执行结束时间")
    run_test_suit_times = db.Column(db.String(100), default=0, comment="测试集执行用时")

    test_case_log = db.relationship('TestCaseLog',order_by='TestCaseLog.action_start_time')

class TestCaseLog(db.Model):
    __tablename__ = 'test_case_log'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    test_case_id = db.Column(db.Integer, comment="测试用例ID")
    test_case_title = db.Column(db.String(100), nullable=False, comment="测试用例标题")
    test_case_suit_log_id = db.Column(db.Integer, db.ForeignKey('test_case_suit_log.id'), comment="所属测试集日志ID")
    run_test_case_result = db.Column(db.Integer, default=0, comment="测试用例操作执行结果:0失败,1成功")
    action_start_time = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"), comment="测试用例开始时间")
    action_end_time = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),comment="测试用例结束时间")
    run_test_case_times = db.Column(db.String(100), default=0, comment="测试用例执行用时")
    test_case_step_log = db.relationship('TestCaseStepLog', order_by='TestCaseStepLog.action_start_time')

class TestCaseStepLog(db.Model):
    __tablename__ = 'test_case_step_log'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    test_case_step_rank = db.Column(db.Integer, comment="测试用例步骤")
    test_case_action_title = db.Column(db.String(100), nullable=False, comment="测试操作标题")
    test_case_action_input = db.Column(db.String(100), nullable=True, comment="测试操作输入参数")
    test_case_action_output = db.Column(db.String(100), nullable=True, comment="测试操作输出参数")
    test_case_log_id = db.Column(db.Integer, db.ForeignKey('test_case_log.id'), comment="所属用例日志ID")
    run_test_action_result = db.Column(db.Integer, nullable=True, comment="测试操作执行结果:0失败,1成功")
    action_start_time = db.Column(db.DateTime,  comment="测试步骤开始时间")
    action_end_time = db.Column(db.DateTime, comment="测试步骤结束时间")
    run_test_case_times = db.Column(db.String(100), default=0, comment="测试步骤执行用时")
    error_msg = db.Column(db.Text,nullable=True, comment="错误信息")

