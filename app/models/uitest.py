from ext import db



# APP页面表
class Page(db.Model):
    __tablename__ = 'page'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, comment="页面名")
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), comment="项目id")
    parent_directory = db.Column(db.Integer, nullable=False, default=0, comment="父级目录ID")
    is_del = db.Column(db.Integer, nullable=False, default=0, comment="是否已删除")
    create_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"), comment="创建时间")
    update_datetime = db.Column(db.DateTime, nullable=False,
                                server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间")
    action = db.relationship('Action', backref=db.backref('page'))
# 元素信息表
class Element(db.Model):
    __tablename__ = 'element'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, comment="目录名")
    type_for_android = db.Column(db.String(30), comment="Android查找方式")
    loc_for_android = db.Column(db.String(200), comment="Android信息描述")
    type_for_ios = db.Column(db.String(30), comment="IOS查找方式")
    loc_for_ios = db.Column(db.String(200), comment="IOS信息描述")
    page_id = db.Column(db.Integer,db.ForeignKey('page.id'), comment="所属页面ID")
    create_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"), comment="创建时间")
    update_datetime = db.Column(db.DateTime, nullable=False,                                server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间")
    page = db.relationship('Page', backref=db.backref('element') )

# 操作表
class Action(db.Model):
    __tablename__ = 'action'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fun_id = db.Column(db.Integer, db.ForeignKey('function_info.id'),nullable=False, comment="方法id")
    ele_id = db.Column(db.Integer, db.ForeignKey('element.id'),comment="所操作元素id")
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'), comment="所属页面ID")
    create_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"), comment="创建时间")
    update_datetime = db.Column(db.DateTime, nullable=False,
                                server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间")
    fun = db.relationship('FunctionInfo')
    ele = db.relationship('Element')
# 方法表
class FunctionInfo(db.Model):
    __tablename__ = 'function_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, unique=True, comment="方法名")
    fun_title = db.Column(db.String(100), nullable=False, unique=True, comment="方法名")
    type = db.Column(db.Integer, comment="所属系统：0通用，1:Android，2:IOS，3:PC")
    description = db.Column(db.String(100), comment="方法说明")
    create_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"), comment="创建时间")
    update_datetime = db.Column(db.DateTime, nullable=False,
                                server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间")

# 用例表
class TestCase(db.Model):
    __tablename__ = 'test_case'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, comment="用例名")
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), comment="所属项目ID")
    is_del = db.Column(db.Integer, nullable=False, default=0, comment="是否已删除")
    parent_directory = db.Column(db.Integer, nullable=False, default=0,comment="父级目录ID")
    create_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"), comment="创建时间")
    update_datetime = db.Column(db.DateTime, nullable=False,
                                server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间")
    step = db.relationship('TestCaseStep', backref=db.backref('test_case'), order_by='TestCaseStep.rank')

# 用例步骤表
class TestCaseStep(db.Model):
    __tablename__ = 'test_case_step'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rank = db.Column(db.Integer, nullable=False, comment="步骤")
    title = db.Column(db.String(100) ,   comment="用例步骤名称")
    action_id = db.Column(db.Integer ,  db.ForeignKey('action.id'), nullable=False,  comment="执行动作")
    skip = db.Column(db.Integer, nullable=False, comment="是否略过")
    take_screen_shot = db.Column(db.Integer, default=0,nullable=False, comment="是否截图")
    wait_time = db.Column(db.Integer, default=0,nullable=False, comment="用例等待时间")
    input_key = db.Column(db.String(100) ,   comment="输入参数名称")
    output_key = db.Column(db.String(100) ,   comment="输出参数名称")
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_case.id'), comment="所属用例ID")
    create_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"), comment="创建时间")
    update_datetime = db.Column(db.DateTime, nullable=False,
                                server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间")
    action = db.relationship('Action', backref=db.backref('step'))

# 用例集
class TestCaseSuit(db.Model):
    __tablename__ = 'test_case_suit'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, comment="用例集名")
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), comment="所属项目ID")
    is_del = db.Column(db.Integer, nullable=False, default=0, comment="是否已删除")
    parent_directory = db.Column(db.Integer, nullable=False, default=0, comment="父级目录ID")
    create_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"), comment="创建时间")
    update_datetime = db.Column(db.DateTime, nullable=False,
                                server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间")
    suit_step = db.relationship('TestSuitStep', backref=db.backref('case_suit'), order_by='TestSuitStep.rank')

# 用例集步骤表
class TestSuitStep(db.Model):
    __tablename__ = 'test_suit_step'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rank = db.Column(db.Integer, nullable=False, comment="执行顺序")
    test_case_id = db.Column(db.Integer ,  db.ForeignKey('test_case.id'), nullable=False,  comment="用例")
    skip = db.Column(db.Integer ,  nullable=False,  comment="是否略过")
    test_case_suit_id = db.Column(db.Integer, db.ForeignKey('test_case_suit.id'), comment="所属用例集ID")
    input_args = db.Column(db.Text, comment="输入参数对象")
    create_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"), comment="创建时间")
    update_datetime = db.Column(db.DateTime, nullable=False,
                                server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间")
    test_case = db.relationship('TestCase',backref=db.backref('suit'))

