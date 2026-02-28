-- 创建数据库
CREATE DATABASE IF NOT EXISTS GongXuKu;

-- 使用创建的数据库
USE GongXuKu;

-- 创建表
CREATE TABLE IF NOT EXISTS Parts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    part_code VARCHAR(50) COMMENT '部件代码',
    part_name VARCHAR(1024) COMMENT '部件名称',
    work_time_sec INT COMMENT '工时/秒',
    processing_fee DECIMAL(10,2) COMMENT '加工费(元)'
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='部件表';

-- 插入数据
INSERT INTO Parts (part_code, part_name, work_time_sec, processing_fee) VALUES
('LING1041', '拉U形领叉捆条*1（20cm）', 26, 0.15),
('LING1019', '拉前V捆条, 订鸡心', 39, 0.23),
('LING1031', '拉后V捆条，定鸡心', 39, 0.23),
('LING1033', '拉前领捆条*1（30cm)', 27, 0.16),
('LING1034', '拉前领捆*2（10cm)', 41, 0.24),
('LING1023', '拉后领捆条*1 (20cm）', 26, 0.15),
('LING1037', '拉后领捆*2（10CM)', 38, 0.22),
('LING1029', '拉前后领捆*2（25cm）', 46, 0.27),
('ZUHE0034', '拉前胸口捆条，交叉固定两侧*2', 81, 0.47),
('LING1001', '拉领捆条，圆领，封苏（50cm）', 45, 0.26),
('LING1006', '拉领捆条*1（50cm）', 33, 0.19),
('LING1003', '拉领捆条，折定领捆两头（50cm）', 53, 0.31),
('LING1026', '拉领捆条，塞头封口（50cm）', 65, 0.38),
('LING1022', '拉领捆条，塞头封口（剪落扣耳）50cm', 74, 0.43),
('LING1048', '拉领捆条，折定领捆两头（剪落扣耳）（50cm）', 65, 0.38),
('LING1018', '拉领捆条，塞头封口（剪落流苏领绳）50cm', 77, 0.45),
('LING1002', '拉领捆条连一侧夹圈，封苏（80cm）', 53, 0.31),
('LING1046', '拉领捆条留空（前领留空一段，封苏）', 51, 0.3),
('LING1040', '拉领捆条留空（落空直出捆条，驳捆条，封苏）', 67, 0.39),
('LING1020', '拉领捆直出绑带（塞头，封口）', 79, 0.46),
('LING1005', '拉领捆条，V领，封苏，定鸡心（70cm）', 63, 0.37),
('LING1008', '拉领捆条，前后V，封苏，定鸡心 130cm', 89, 0.52),
('LING1007', '拉领捆条，V领，封苏，定鸡心，前V订捆条横连（70cm）', 132, 0.77),
('LING1010', '拉领捆条，封苏（U形领）100cm', 58, 0.34),
('LING1011', '拉领捆，U形领（封苏，定鸡心4点）100cm', 113, 0.66),
('LING1004', '拉领捆条，封苏，后U订交叉捆条（80cm）', 130, 0.76),
('LING1042', '拉前襟连领捆条*1 （100cm）', 46, 0.27),
('LING1027', '拉前襟连领捆条，交叉固定前腰', 57, 0.33),
('LING1052', '拉前襟连领捆条，交叉固定前腰（120cm）', 65, 0.38),
('LING1009', '拉领捆条连前襟，V领（拷散口，搭车合前片）', 91, 0.53),
('LING1043', '拉前襟连领内捆*1（100cm）', 149, 0.87),
('LING1028', '拉前襟连领内捆条，交叉固定前腰', 130, 0.76),
('LING1053', '拉前襟连领内捆，交叉固定前腰（120cm）', 144, 0.84),
('LING1015', '拉领内捆连前襟，V领（拷散口，搭车合前片）', 194, 1.13),
('LING1035', '拉前领内捆*1（30cm）', 69, 0.4),
('LING1036', '拉前领内捆*2（10cm）', 72, 0.42),
('LING1024', '拉后领内捆*1（20cm）', 58, 0.34),
('LING1025', '拉后领内捆*1，运反两头 （20cm）', 82, 0.48),
('LING1038', '拉后领内捆*2（10cm)', 72, 0.42),
('LING1030', '拉前后领内捆条*2（25cm）', 106, 0.62),
('LING1044', '拉领内捆条（50cm）', 91, 0.53),
('LING1013', '拉领内捆条，圆领，封苏（50cm）', 103, 0.6),
('LING1056', '拉领内捆条，驳接封口*1（50cm）', 125, 0.73),
('LING1021', '拉领内捆条（剪落扣耳）50cm', 103, 0.6),
('LING1014', '拉领内捆条，V领，封苏，定鸡心 70cm', 139, 0.81),
('LING1016', '拉领内捆条，V领（定鸡心，后露背，系带捆条）', 264, 1.54),
('LING1017', '拉领内捆条，U形领，封苏 ，定鸡心4点，80cm', 194, 1.13),
('LING3033', '走定领面里*1（90cm）', 31, 0.18),
('LING3034', '环间领口*1（60cm）', 33, 0.19),
('LING3027', '折冚领（50cm）', 26, 0.15),
('LING3029', '拷领口，折冚领（50cm）', 39, 0.23),
('LING3055', '拷领口（50cm）', 14, 0.08),
('LING3056', '拷领口，折定2点（50cm）', 34, 0.2),
('LING3053', '拷领口，折间（60cm）', 43, 0.25),
('LING3028', '密拷领口', 21, 0.12),
('ZUHE109', '密拷领口，袖口，下摆', 81, 0.47),
('LING3061', '密拷裁片，剪落领橡筋*1（30cm）', 43, 0.25),
('LING3047', '密拷前后领，剪落领橡筋*2（30cm）', 74, 0.43),
('LING3048', '密拷领，剪落橡筋*1 (100cm)', 96, 0.56),
('LING2001', '圆领，四线上领', 45, 0.26),
('LING2003', '圆领，四线上领，后领捆', 103, 0.6),
('LING2043', '圆领，四线上领，间后领线', 62, 0.36),
('LING2049', '圆领，四线上领，间线一周', 72, 0.42),
('LING2004', '圆领，四线上领，后领捆，间前领线', 123, 0.72),
('LING2097', '圆领，四线上领，间前领线，双线拉肩连后领贴条', 99, 0.58),
('LING2002', '圆领，四线上领，冚领线一周', 65, 0.38),
('LING2138', '圆领，四线上领，后领捆，冚前领线', 147, 0.86),
('YUND132', '运动：圆领，四线上领，贴后领织带，冚前领     （此工序无滴针）', 120, 0.7),
('LING2116', '高领，四线上领（领高8cm）*1', 65, 0.38),
('LING2017', '高领，四线上领（运反领顶，间暗线）', 147, 0.86),
('LING2053', '落空圆领', 86, 0.5),
('LING2037', '扁机领，全领内捆条', 117, 0.68),
('LING2035', '2片领塞棉', 209, 1.22),
('LING2131', '西装领，间明线（套里）', 259, 1.51);


DROP TABLE IF EXISTS `Template`;
-- 创建表
CREATE TABLE Template (
    id INT AUTO_INCREMENT PRIMARY KEY,
    part_code VARCHAR(50) COMMENT '部件代码',
    part_name VARCHAR(1024) COMMENT '部件名称',
    unit_price DECIMAL(10, 2) COMMENT '单价',
    time_seconds INT COMMENT '时间(秒)',
    difficulty CHAR(5) COMMENT '难度'
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='大货生产工序表';

-- 插入数据
INSERT INTO Template (part_code, part_name, unit_price, time_seconds, difficulty) VALUES
('LING2037', '扁机领，全领内捆条', 0.58, 117, 'C'),
('LING2035', '2片领塞棉', 1.11, 209, NULL),
('LING2131', '西装领，间明线（套里）', 1.53, 259, 'B');

DROP TABLE IF EXISTS `processes`;
-- 创建表
CREATE TABLE processes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sequence INT COMMENT '序号',
    machine_type VARCHAR(50) COMMENT '车种',
    action_desc VARCHAR(100) COMMENT '动作描述',
    length_range VARCHAR(50) COMMENT '长度',
    level CHAR(5) COMMENT '级别',
    frequency INT COMMENT '频率',
    calculated_value DECIMAL(5,4) COMMENT '计算',
    time_cost INT COMMENT '时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='子工序主表';

-- 插入数据
INSERT INTO processes (sequence, machine_type, action_desc, length_range, level, frequency, calculated_value, time_cost) VALUES
(1, '手工', '点位剪口', '0-9', 'a', 1, 0.015, 3),
(2, '平车', '合缝', '0-9', 'a', 1, 0.0567, 11),
(3, '三线', '散口', '40-49', 'a', 1, 0.099, 20),
(4, '平车', '散口', '40-49', 'a', 1, 0.1386, 28);

DROP TABLE IF EXISTS `Master`;
-- 创建主表存储所有下拉框选项
CREATE TABLE Master (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category ENUM('车种','动作描述','长度','级别','频率') NOT NULL COMMENT '分类类型',
    value VARCHAR(50) NOT NULL COMMENT '选项值',
    sort_order INT DEFAULT 0 COMMENT '排序序号',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY uk_category_value (category, value),
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='下拉框值表';

--  插入车种数据
INSERT INTO Master (category, value, sort_order) VALUES
('车种', '平车', 1),('车种', '三线', 2),('车种', '四线', 3),
('车种', '五线', 4),('车种', '双针', 5),('车种', '冚车', 6),
('车种', '虾苏', 7),('车种', '手工', 8),('车种', '打枣', 9),
('车种', '埋夹', 10),('车种', '裤头', 11),('车种', '挑脚', 12),
('车种', '人字', 13),('车种', '中烫', 14),('车种', '四针六线', 15);

-- 插入动作描述数据
INSERT INTO Master (category, value, sort_order) VALUES
('动作描述', '合缝', 1),('动作描述', '间线', 2),
('动作描述', '散口', 3),('动作描述', '走定走缩', 4),
('动作描述', '漏坑', 5),('动作描述', '点位剪口', 6),
('动作描述', '中烫', 7),('动作描述', '搭车', 8),
('动作描述', '密拷', 9),('动作描述', '环口', 10);

-- 插入长度范围数据(使用批量生成方式)
INSERT INTO Master (category, value, sort_order)
SELECT '长度', CONCAT((n*10),'-',(n*10+9)), n+1
FROM (
    SELECT 0 AS n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3
    UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7
    UNION SELECT 8 UNION SELECT 9 UNION SELECT 10 UNION SELECT 11
    UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION SELECT 15
    UNION SELECT 16 UNION SELECT 17 UNION SELECT 18 UNION SELECT 19
) AS numbers;

-- 插入级别数据
INSERT INTO Master (category, value, sort_order) VALUES
('级别', 'a', 1),('级别', 'b', 2),('级别', 'c', 3),
('级别', 'd', 4),('级别', 'e', 5);

-- 插入频率数据(使用存储过程批量插入)
INSERT INTO Master (category, value, sort_order) VALUES
('频率', '1', 1),('频率', '2', 2),('频率', '3', 3),
('频率', '4', 4),('频率', '5', 5),('频率', '6', 6),('频率', '7', 7),('频率', '8', 8),
('频率', '9', 9),('频率', '10', 10),('频率', '11', 11),('频率', '12', 12),('频率', '13', 13),
('频率', '14', 14),('频率', '15', 15),('频率', '16', 16),('频率', '17', 17),('频率', '18', 18),
('频率', '19', 19),('频率', '20', 20),('频率', '21', 21),('频率', '22', 22),('频率', '23', 23),
('频率', '24', 24),('频率', '25', 25),('频率', '26', 26),('频率', '27', 27),('频率', '28', 28),
('频率', '29', 29),('频率', '30', 30),('频率', '31', 31),('频率', '32', 32),('频率', '33', 33),
('频率', '34', 34),('频率', '35', 35),('频率', '36', 36),('频率', '37', 37),('频率', '38', 38),
('频率', '39', 39),('频率', '40', 40),('频率', '41', 41),('频率', '42', 42),('频率', '43', 43),
('频率', '44', 44),('频率', '45', 45),('频率', '46', 46),('频率', '47', 47),('频率', '48', 48),
('频率', '49', 49),('频率', '50', 50);

-- 创建统一参数表
CREATE TABLE Calculated (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category ENUM('车种', '动作', '级别', '长度') NOT NULL,
    param_key VARCHAR(20) NOT NULL,
    param_value DECIMAL(10,5) NOT NULL,
    UNIQUE KEY (category, param_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='下拉框值对应的计算值';

INSERT INTO Calculated (category, param_key, param_value) VALUES
('车种', '挑脚', 1.6),
('车种', '中烫', 2),
('车种', '四针六线', 1.8),
('车种', '人字', 1.7),
('车种', '裤头', 1.2),
('车种', '埋夹', 1.3),
('车种', '打枣', 1.2),
('车种', '虾苏', 1.7),
('车种', '五线', 1.3),
('车种', '冚车', 1.5),
('车种', '四线', 1.2),
('车种', '双针', 1.7),
('车种', '手工', 1),
('车种', '平车', 1.4),
('车种', '三线', 1),
('动作', '环口', 3.7),
('动作', '密拷', 2.8),
('动作', '搭车', 3.8),
('动作', '中烫', 1.3),
('动作', '漏坑', 5),
('动作', '走定走缩', 2.2),
('动作', '点位剪口', 1),
('动作', '合缝', 2.7),
('动作', '散口', 2.2),
('动作', '间线', 3.2),
('级别', 'a', 0.005),
('级别', 'b', 0.0053),
('级别', 'c', 0.0059),
('级别', 'd', 0.0064),
('级别', 'e', 0.0094),
('长度', '0-9', 3),
('长度', '10-19', 5),
('长度', '20-29', 6),
('长度', '30-39', 7),
('长度', '40-49', 9),
('长度', '50-59', 11),
('长度', '60-69', 13),
('长度', '70-79', 15),
('长度', '80-89', 17),
('长度', '90-99', 19),
('长度', '100-109', 21),
('长度', '110-119', 23),
('长度', '120-129', 25),
('长度', '130-139', 27),
('长度', '140-149', 29),
('长度', '150-159', 31),
('长度', '160-169', 33),
('长度', '170-179', 35),
('长度', '180-189', 37),
('长度', '190-199', 39);
