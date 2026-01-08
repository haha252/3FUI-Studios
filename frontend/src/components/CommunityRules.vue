<script setup>
import { ArrowLeftIcon } from '@heroicons/vue/24/outline'

const emit = defineEmits(['go-back'])
</script>

<template>
  <div class="max-w-4xl mx-auto text-gray-300 leading-relaxed space-y-12 pb-16 pt-16">
    <!-- Header / Back Button -->
    <div class="mb-8">
      <button 
        @click="emit('go-back')"
        class="flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-4"
      >
        <ArrowLeftIcon class="w-5 h-5" />
        <span>返回首页</span>
      </button>
      <h1 class="text-3xl font-bold text-gray-100 flex items-center gap-3">
        3FUI Studios <span class="text-gray-500 font-normal">社区规则</span>
      </h1>
    </div>

    <!-- 参与须知 -->
    <section>
      <h2 class="text-2xl font-bold text-gray-100 mb-4">参与须知</h2>
      <p class="text-gray-400">
        3FUI Studios 是一个纯民间的活动项目，禁止职业选手参赛，禁止使用任何纯商业和未发布的软件，仅允许 FFmpeg 和其他开源软件。我们做这个只是自娱自乐，不代表任何官方观点，也不与任何专业团队有关系。
      </p>
    </section>

    <!-- 如何发布 -->
    <section>
      <h2 class="text-2xl font-bold text-gray-100 mb-4">如何发布</h2>
      <p class="text-gray-400 mb-4">
        你需要一个 GitHub 账号来提交更改。首先将你的文件存放至我们支持筛选的平台上，然后到按照 README 文件中的规范向仓库提交数据文件的更新，等待我们人工审核之后便可以直接加入，可以加入 3FUI 群并提供内容截图来加速审核。
      </p>
      <p class="text-gray-400">
        请注意：<span class="text-orange-400">禁止加密、伪装、打压缩包、改后缀等行为，所有内容必须接受所有人的检查，也禁止有任何盈利和商业行为。</span>
      </p>
    </section>

    <!-- 内容限制 -->
    <section>
      <h2 class="text-2xl font-bold text-gray-100 mb-4">内容限制</h2>
      <p class="text-gray-400 mb-4">
        这里不是自由发布影视资源的地方，也不是分享私人生活的地方。我们拒绝所有版权受限、非法和私人内容，一旦接到投诉我们会立刻移除，如发现故意提交这类内容的将直接除名。
      </p>
      <div class="space-y-2 mb-4">
        <p>
          <span class="text-orange-500 font-bold">总的来说，这些内容是绝对不允许的：</span>
          <span class="text-orange-400">正在上映的电影、版权敏感的电影、独播的电视剧、所有电视节目、任何短视频、监控。</span>
        </p>
        <p>
          <span class="text-green-500 font-bold">明确地讲，我们推荐这些类型的内容：</span>
          <span class="text-green-400">已完结的番剧、老电影、小众电影、早期动画、游戏CG、纪录片、3D 渲染、线下活动。</span>
        </p>
      </div>
      <p class="text-gray-400">
        关于字幕：除非已获授权否则全面禁止包含字幕(包括烧录)。
      </p>
    </section>

    <!-- 技术要求 -->
    <section>
      <h2 class="text-2xl font-bold text-gray-100 mb-4">技术要求</h2>
      <p class="mb-4">
        我们的目标是：<span class="text-pink-500 font-medium">在保证视觉质量的前提下压出最低文件体积</span>。这与专业压制组有很大不同。
      </p>
      <ul class="list-disc pl-5 space-y-2 text-gray-400">
        <li>任何能够肉眼看到质量损失的结果都是不合格的</li>
        <li>我们允许使用显卡压制，因为我们不是专业压制组</li>
        <li>我们允许使用各种处理和后期制作，包括AI；但请注意：任何肉眼可见的果冻也是不合格的</li>
        <li>禁止开挂，禁止使用超算，禁止使用云计算平台的转码服务；但可以用常规服务器(含集群)</li>
        <li>不要耍小聪明，使用流媒体平台压制的一律不合格</li>
      </ul>
    </section>

    <!-- 标题命名规范 -->
    <section>
      <h2 class="text-2xl font-bold text-gray-100 mb-4">标题命名规范</h2>
      <p class="text-gray-400 mb-4">
        由于我们不存储任何图片和高级描述，因此标题的格式是非常重要的，请务必按照规范提供
      </p>
      
      <div class="bg-[#1e1e1e] border border-gray-700 p-4 rounded mb-6 font-mono text-sm text-blue-300 break-all">
        [文件大小].[编码器].中文名.源本土原名.分辨率.高帧值.8/10bit.S/HDR.[音频编码].声道数_其他信息
      </div>

      <p class="text-gray-400 mb-4">
        这看上去与专业压制组的命名很像，最大的区别是 <span class="text-pink-500">带方括号的编码器名称和文件大小</span>；
        编码器必须是详细编码器名称，例如 libx265、av1_nvenc 这样的；
        容量大小请使用合适的单位，例如 560M、1.75G；
        高帧值仅高帧率视频填写，低于 48 帧(不含48) 的视频都算常规视频，规范如：50fps、60fps；
        如果是动态帧率，请写vfr最低~最高，例如 vfr1~23.97；
        音频编码跟视频编码一样，也必须写详细编码器名称；
        声道数请写声道布局的名称，例如 mono、stereo、5.1、7.1；
        最后的其他信息可以像专业压制组一样写名字或者写自定义的标记等等。
        另外AI和其他处理标记可以根据美观度自行安排。
      </p>

      <p class="text-gray-400 mb-2">就比如像这样：</p>
      <div class="bg-[#1e1e1e] border border-gray-700 p-4 rounded space-y-2 font-mono text-sm text-gray-300 overflow-x-auto">
        <div>[1.5G].[libx265].星际穿越.Interstellar.1080p.10bit.HDR.[libfdk_aac].5.1_3FUI-Studios</div>
        <div>[2.3G].[av1_nvenc].假设一个名字.1080p.8bit.SDR.TopazAI.[libfdk_aac].stereo.Mix_3FUI-Studios</div>
      </div>

      <p class="text-gray-500 mt-4 text-sm">
        其他信息比如想要标注比特率，请在描述里简单填写
      </p>
    </section>

  </div>
</template>

<style scoped>
/* Optional: Add custom selection color or transitions if needed */
</style>
