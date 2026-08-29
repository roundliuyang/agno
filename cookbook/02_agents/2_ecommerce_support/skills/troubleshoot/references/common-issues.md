# 常见问题与解决方案

## 登录问题

### "Invalid credentials"（凭证无效）错误
1. 确认邮箱地址正确（检查是否有拼写错误）
2. 尝试重置密码：Settings > Account > Reset Password
3. 检查账号是否被锁定（连续 5 次失败会触发 15 分钟锁定）
4. 清除浏览器缓存和 Cookie，重新尝试
5. 如果使用 SSO 单点登录，请联系 IT 管理员确认 SSO 配置正确

### 登录后提示 "Session expired"（会话过期）
1. 检查浏览器 Cookie 设置（必须允许第三方 Cookie）
2. 禁用可能阻止 Cookie 的浏览器扩展（如 Privacy Badger 等）
3. 尝试使用无痕/隐私浏览模式
4. 如果持续出现，检查系统时钟是否同步

## 同步问题

### 文件无法同步
1. 检查网络连接
2. 查看存储配额：Settings > Storage（如果已满，同步会暂停）
3. 检查文件是否超过大小限制（Pro 版单文件 100 MB，Enterprise 版 500 MB）
4. 重启桌面客户端：系统托盘 > 右键 > Restart
5. 查看同步日志：Help > Diagnostics > Sync Log

### 同步冲突处理
- 默认以最近一次编辑为准
- 冲突副本保存为 "[文件名] (conflict copy).ext"
- 在 Settings > Sync > Conflict History 中查看冲突记录

## 性能问题

### 加载缓慢
1. 检查当前服务状态（使用状态检查脚本）
2. 换一个浏览器测试，排除扩展干扰
3. 清除本地缓存：Settings > Advanced > Clear Cache
4. 检查网速（最低建议 5 Mbps）

### 内存占用过高
1. 关闭未使用的标签页/项目
2. 如不需要，禁用实时协作功能
3. 降低同步频率：Settings > Sync > Update Interval

## 工单升级

如果以上步骤未能解决问题，请创建支持工单：
- **Subject（主题）**: [问题类别] - 简要描述
- **Body（正文）**: 已尝试的步骤、错误信息（截图）、账号邮箱
- **Priority（优先级）**: P1（服务不可用）、P2（主要功能故障）、P3（小问题）
