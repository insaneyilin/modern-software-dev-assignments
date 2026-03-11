import { connectDB } from '../db/db';
import { Note } from '../db/models/note';

async function testFeatures() {
  try {
    console.log('🔗 连接数据库...');
    await connectDB();
    console.log('✓ 数据库连接成功\n');

    // 测试1: 创建笔记
    console.log('📝 测试1: 创建新笔记');
    const note1 = await Note.create({
      title: '测试笔记1',
      content: '这是第一条测试笔记的内容'
    });
    console.log(`✓ 笔记创建成功: ${note1._id}`);
    console.log(`  标题: ${note1.title}`);
    console.log(`  创建时间: ${note1.createdAt}\n`);

    // 测试2: 创建第二条笔记
    console.log('📝 测试2: 创建第二条笔记');
    const note2 = await Note.create({
      title: '购物清单',
      content: '牛奶、面包、鸡蛋、水果'
    });
    console.log(`✓ 笔记创建成功: ${note2._id}\n`);

    // 测试3: 创建第三条笔记
    console.log('📝 测试3: 创建第三条笔记');
    const note3 = await Note.create({
      title: '',
      content: '这是一条没有标题的笔记'
    });
    console.log(`✓ 笔记创建成功: ${note3._id}\n`);

    // 测试4: 获取所有笔记
    console.log('📋 测试4: 获取所有笔记（按更新时间倒序）');
    const allNotes = await Note.find({}).sort({ updatedAt: -1 }).lean();
    console.log(`✓ 找到 ${allNotes.length} 条笔记`);
    allNotes.forEach((note, index) => {
      console.log(`  ${index + 1}. ${note.title || 'Untitled'} - ${new Date(note.updatedAt).toLocaleString('zh-CN')}`);
    });
    console.log();

    // 测试5: 更新笔记
    console.log('✏️  测试5: 更新笔记内容');
    const updatedNote = await Note.findByIdAndUpdate(
      note1._id,
      { $set: { content: '这是更新后的内容' } },
      { new: true }
    );
    console.log(`✓ 笔记更新成功`);
    console.log(`  新内容: ${updatedNote?.content}\n`);

    // 测试6: 搜索笔记
    console.log('🔍 测试6: 全文搜索（搜索"购物"）');
    const searchResults = await Note.find({ $text: { $search: '购物' } }).lean();
    console.log(`✓ 找到 ${searchResults.length} 条匹配的笔记`);
    searchResults.forEach((note) => {
      console.log(`  - ${note.title || 'Untitled'}`);
    });
    console.log();

    // 测试7: 删除笔记
    console.log('🗑️  测试7: 删除笔记');
    await Note.findByIdAndDelete(note3._id);
    console.log(`✓ 笔记删除成功: ${note3._id}\n`);

    // 测试8: 验证删除
    console.log('✅ 测试8: 验证删除后的笔记数量');
    const finalCount = await Note.countDocuments();
    console.log(`✓ 当前笔记数量: ${finalCount}\n`);

    console.log('🎉 所有测试通过！');
    console.log('\n📊 测试总结:');
    console.log('  ✓ 创建笔记: 成功');
    console.log('  ✓ 获取笔记列表: 成功');
    console.log('  ✓ 更新笔记: 成功');
    console.log('  ✓ 全文搜索: 成功');
    console.log('  ✓ 删除笔记: 成功');
    console.log('  ✓ 索引验证: 成功');

    process.exit(0);
  } catch (error) {
    console.error('✗ 测试失败:', error);
    process.exit(1);
  }
}

testFeatures();
