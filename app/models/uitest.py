from ext import db


# APP页面表
class Page(db.Model):
    __tablename__ = 'page'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, comment="页面名")
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), comment="项目id")
    create_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"), comment="创建时间")
    update_datetime = db.Column(db.DateTime, nullable=False,
                                server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间")
    project = db.relationship('Project', backref=db.backref('page'))

# 元素信息表
class Element(db.Model):
    __tablename__ = 'element'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, comment="目录名")
    type = db.Column(db.String(30), comment="查找方式")
    loc = db.Column(db.String(200), comment="信息描述")
    page_id = db.Column(db.Integer,db.ForeignKey('page.id'), comment="所属页面ID")
    create_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"), comment="创建时间")
    update_datetime = db.Column(db.DateTime, nullable=False,                                server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间")
    page = db.relationship('Page', backref=db.backref('element'))

# 操作表
class Action(db.Model):
    __tablename__ = 'action'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, comment="执行操作名称")
    fun_id = db.Column(db.Integer, nullable=False, comment="方法id")
    ele_id = db.Column(db.Integer, comment="所操作元素id")
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'), comment="所属页面ID")
    create_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"), comment="创建时间")
    update_datetime = db.Column(db.DateTime, nullable=False,
                                server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间")
    page = db.relationship('Page', backref=db.backref('action'))

# 方法表
class FunctionInfo(db.Model):
    __tablename__ = 'function_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, unique=True, comment="方法名")
    type = db.Column(db.Integer, comment="所属系统：通用，1:Android，2:IOS，3:PC")
    description = db.Column(db.String(100), comment="方法说明")
    create_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"), comment="创建时间")
    update_datetime = db.Column(db.DateTime, nullable=False,
                                server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间")

# 用例表
class TestCase(db.Model):
    __tablename__ = 'test_case'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, comment="用例名")
    action_id = db.Column(db.Integer, comment="用例步骤id，关联action表")
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), comment="所属项目ID")

    create_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"), comment="创建时间")
    update_datetime = db.Column(db.DateTime, nullable=False,
                                server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间")
    project = db.relationship('Project', backref=db.backref('test_case'))

# 用例集
class TestCaseSuit(db.Model):
    __tablename__ = 'test_case_suit'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, comment="用例集名")
    test_case_ids = db.Column(db.String(100), nullable=False, comment="包含的用例ID")
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), comment="所属项目ID")
    description = db.Column(db.String(100), comment="说明")
    create_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"), comment="创建时间")
    update_datetime = db.Column(db.DateTime, nullable=False,
                                server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间")
    project = db.relationship('Project', backref=db.backref('test_case_suit'))

# # 接口表
# class Request_api(db.Model):
#     __tablename__ = 'request_api'
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     req_name = db.Column(db.String(100), nullable=False)
#     project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False, )
#     req_method = db.Column(db.String(100), nullable=False)
#     req_url = db.Column(db.String(100), nullable=False)
#     req_data = db.Column(db.Text)
#     create_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"), comment="创建时间")
#     update_datetime = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间")
#     # 在Req_api可以通过project(关系名称)关联到project表根据project_id, 同时在Project表也可以通过api,关联到Comment表
#     project = db.relationship('Project', backref=db.backref('request_api', order_by=create_datetime.desc()))
#
#
