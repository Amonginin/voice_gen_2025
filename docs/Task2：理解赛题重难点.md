<font style="color:rgb(31, 35, 41);background-color:rgb(240, 244, 255);">💡</font>

<font style="color:rgb(31, 35, 41);background-color:rgb(240, 244, 255);">欢迎来到Datawhale AI夏令营第三期，</font>**<font style="color:rgb(31, 35, 41);background-color:rgb(240, 244, 255);">全球AI攻防挑战赛（语音生成方向）</font>**<font style="color:rgb(31, 35, 41);background-color:rgb(240, 244, 255);">方向的学习~</font>

<font style="color:rgb(31, 35, 41);background-color:rgb(240, 244, 255);">我们将聚焦在「</font>[<font style="color:rgb(51, 109, 244);background-color:rgb(240, 244, 255);">2025全球AI攻防挑战赛：泛终端智能语音交互认证-生成赛</font>](https://tianchi.aliyun.com/s/cf5e086cbcc968d7f090a8b3d5eb34ab)<font style="color:rgb(31, 35, 41);background-color:rgb(240, 244, 255);">」的赛事项目实践。</font>

**<font style="color:rgb(216, 57, 49);background-color:rgb(240, 244, 255);">本次项目实践中，你写的每一行代码，都在为全球语音安全防线铸造新的盾牌！</font>**

**<font style="color:rgb(216, 57, 49);background-color:rgb(240, 244, 255);">建造「AI防伪训练场」：</font>**<font style="color:rgb(216, 57, 49);background-color:rgb(240, 244, 255);">〖 用顶级黑客思维 〗→ 生成足以乱真的克隆语音 → 〖 暴露所有防御弱点 〗→ 〖 倒逼防御系统进化 〗</font>

<font style="color:rgb(31, 35, 41);background-color:rgb(240, 244, 255);">作为此次项目实践的第二个Task，我们将—— </font>**<font style="color:rgb(216, 57, 49);background-color:rgb(240, 244, 255);">理解项目目标、从业务理解到技术实现</font>****<font style="color:rgb(31, 35, 41);background-color:rgb(240, 244, 255);">！</font>**

<font style="color:rgb(31, 35, 41);background-color:rgb(240, 244, 255);">我们只有 </font>**<font style="color:rgb(216, 57, 49);background-color:rgb(240, 244, 255);">理解业务逻辑</font>**<font style="color:rgb(31, 35, 41);background-color:rgb(240, 244, 255);">，才能做出 </font>**<font style="color:rgb(31, 35, 41);background-color:rgb(240, 244, 255);">真正有价值、解决问题的方案！</font>**

# **<font style="color:rgb(31, 35, 41);">一、此次项目是一个语音生成类任务</font>**
<font style="color:rgb(31, 35, 41);background-color:rgb(255, 245, 235);">💡</font>

<font style="color:rgb(31, 35, 41);background-color:rgb(255, 245, 235);">本赛题为AI语音攻防赛道的生成阶段，参赛队伍可以根据给定的文本和参考音频，以高自然度、高相似度为目标生成对应的伪造语音</font>

**<font style="background-color:rgba(255, 246, 122, 0.8);">相关知识点清单</font>**

**<font style="color:rgb(31, 35, 41);">TTS 系统基本架构</font>**<font style="color:rgb(31, 35, 41);"> : 文本前端（Text Front-end）-> 声学模型（Acoustic Model）-> 声码器（Vocoder）。</font>

**<font style="color:rgb(31, 35, 41);">说话人嵌入 (Speaker Embedding)</font>**<font style="color:rgb(31, 35, 41);"> : 通过预训练的声纹识别模型（如 X-vector, ECAPA-TDNN）或自监督模型（如 WavLM, HuBERT）提取，用于编码说话人音色信息。</font>

**<font style="color:rgb(31, 35, 41);">风格迁移/多说话人 TTS</font>**<font style="color:rgb(31, 35, 41);"> : 训练模型学习多个说话人的音色，并能够根据参考语音（或说话人嵌入）生成指定说话人的语音。</font>

**<font style="color:rgb(31, 35, 41);">条件生成</font>**<font style="color:rgb(31, 35, 41);"> : 如何有效利用参考语音作为条件，指导合成语音在音色、情感、语速等方面与参考语音保持一致。</font>

+ **<font style="color:rgb(31, 35, 41);">基于编码器-解码器架构</font>**<font style="color:rgb(31, 35, 41);"> : 编码器提取文本特征和说话人特征，解码器生成语音。</font>
+ **<font style="color:rgb(31, 35, 41);">基于扩散模型/流模型</font>**<font style="color:rgb(31, 35, 41);"> : 在生成过程中以参考语音的特征作为条件。</font>
+ **<font style="color:rgb(31, 35, 41);">基于神经网络编解码器 (Neural Codec)</font>**<font style="color:rgb(31, 35, 41);"> : 将语音转换为离散 Token，再用语言模型生成这些 Token（如 VALL-E）。</font>

# **<font style="color:rgb(31, 35, 41);">二、任务要求究竟是怎么样的、以及有哪些重难点呢？</font>**
<font style="color:rgb(31, 35, 41);">比赛的核心任务是 </font>**<font style="color:rgb(31, 35, 41);">生成高度逼真且目标说话人风格一致的合成语音</font>**<font style="color:rgb(31, 35, 41);"> 。</font>

<font style="color:rgb(31, 35, 41);">从“以攻促防”的角度看，参赛者需要最大化生成语音的 </font>**<font style="color:rgb(31, 35, 41);">“欺骗性”</font>**<font style="color:rgb(31, 35, 41);"> ，使其能够骗过目前的语音识别和声纹识别系统，甚至达到人类听觉难以分辨的程度。</font>

## <font style="color:rgb(31, 35, 41);">赛事背景</font>
<font style="color:rgb(31, 35, 41);">比赛要求参赛者以 </font>**<font style="color:rgb(31, 35, 41);">超拟人的自然度和超高的声纹相似度</font>**<font style="color:rgb(31, 35, 41);"> 合成伪造语音。</font>

<font style="color:rgb(31, 35, 41);">这不仅将推动语音生成技术本身的进步，更重要的是，它能帮助我们</font>**<font style="color:rgb(216, 57, 49);">深入了解当前AI语音技术所能达到的“欺骗”最高水平</font>**<font style="color:rgb(31, 35, 41);">，揭示其潜在的攻击能力。</font>

<font style="color:rgb(31, 35, 41);">赛事采取了“ </font>**<font style="color:rgb(31, 35, 41);">以攻促防</font>**<font style="color:rgb(31, 35, 41);"> ”的核心策略。通过集中全球顶尖AI人才来生成最难辨别的合成语音样本，可以 </font>**<font style="color:rgb(31, 35, 41);">暴露现有语音防伪检测技术的弱点和盲区</font>**<font style="color:rgb(31, 35, 41);"> 。</font>

<font style="color:rgb(31, 35, 41);">这些高质量的“攻击”样本将成为宝贵的训练数据和测试用例，促使研究人员和工程师们开发出 </font>**<font style="color:rgb(31, 35, 41);">更先进、更鲁棒的语音防伪检测模型和系统</font>**<font style="color:rgb(31, 35, 41);"> 。</font>

## <font style="color:rgb(31, 35, 41);">赛题解读 与 数据分析</font>
<font style="color:rgb(31, 35, 41);">本次比赛将提供 </font>**<font style="color:rgb(31, 35, 41);">200道 </font>**<font style="color:rgb(31, 35, 41);">赛题作为评测集，每道题目中包含一个待合成文本和一条参考语音。</font>

+ <font style="color:rgb(31, 35, 41);">参赛者需根据给定的文本和参考语音生成对应的合成语音，</font>
    - <font style="color:rgb(31, 35, 41);">该合成语音中的文本内容应当与给定的文本一致，</font>
    - <font style="color:rgb(31, 35, 41);">同时语音中的说话人音色、语音情感等风格特征应当与参考音频中的保持一致。</font>

<font style="color:rgb(31, 35, 41);">本任务不限制训练数据集，选手可使用任意数据集开展模型研发。</font>

<font style="color:rgb(31, 35, 41);">其中参考语音的采集设备包括 </font><u><font style="color:rgb(31, 35, 41);">手机、电脑、录音笔、智能眼镜</font></u><font style="color:rgb(31, 35, 41);">等。</font>

<font style="color:rgb(31, 35, 41);">具体任务文件为</font>`<font style="color:rgb(31, 35, 41);background-color:rgb(245, 246, 247);">aigc_speech_generation_tasks.csv</font>`<font style="color:rgb(31, 35, 41);">，内容示例如下：</font>

<font style="color:rgb(31, 35, 41);">其中"</font>`<font style="color:rgb(31, 35, 41);background-color:rgb(245, 246, 247);">utt</font>`<font style="color:rgb(31, 35, 41);">"列表示题目序号，"</font>`<font style="color:rgb(31, 35, 41);background-color:rgb(245, 246, 247);">reference_speech</font>`<font style="color:rgb(31, 35, 41);">"列表示参考音频，"</font>`<font style="color:rgb(31, 35, 41);background-color:rgb(245, 246, 247);">text</font>`<font style="color:rgb(31, 35, 41);">"列表示待合成文本。</font>

<font style="color:rgb(31, 35, 41);">比赛期间，参赛队伍通过天池平台下载评测数据集，本地调试算法，在线提交结果，结果为一个zip压缩包文件，大小不超过2G，文件名为"</font>`<font style="color:rgb(31, 35, 41);background-color:rgb(245, 246, 247);">参赛队名称-result.zip</font>`<font style="color:rgb(31, 35, 41);">"。</font>

<font style="color:rgb(31, 35, 41);">该压缩包中包括一个结果表格和所有赛题对应的生成结果语音文件。具体文件夹结构如下：</font>

```plain
参赛队名称-result/
├── synthesized_speech_1.wav
├── synthesized_speech_2.wav
├── ......
└── 参赛队名称-result.csv
```

## <font style="color:rgb(31, 35, 41);">赛题要点与难点</font>
**<font style="color:rgb(31, 35, 41);">零样本语音克隆</font>**<font style="color:rgb(31, 35, 41);"> : 只通过一个短参考音频来克隆音色和风格，对模型的泛化能力要求很高。</font>

**<font style="color:rgb(31, 35, 41);">文本-语音对齐与时长控制</font>**<font style="color:rgb(31, 35, 41);"> : 需要将任意长度的文本与根据参考音频克隆出的风格正确地映射到合成语音的时长上，且不能影响自然度。</font>

**<font style="color:rgb(31, 35, 41);">多维度风格迁移</font>**<font style="color:rgb(31, 35, 41);"> : 不仅仅是音色，还包括语速、韵律、情感等多种风格特征的迁移。</font>

**<font style="color:rgb(31, 35, 41);">复杂场景泛化</font>**<font style="color:rgb(31, 35, 41);"> : 参考语音来自不同设备，可能包含噪声或不同的录音条件，模型需要具备一定的鲁棒性。</font>

## <font style="color:rgb(31, 35, 41);">解题思考过程</font>
+ **<font style="color:rgb(31, 35, 41);">零样本 (Zero-shot) TTS</font>**<font style="color:rgb(31, 35, 41);"> : 虽然题目描述没有直接出现“零样本”这个词，但“仅通过3秒的参考音频就能够克隆目标说话人的音色并合成出任意语音”明确指向了零样本语音克隆的能力，这是当前TTS领域的前沿和难点。</font>
+ **<font style="color:rgb(31, 35, 41);">隐含维度 - 防伪模型攻击成功率</font>**<font style="color:rgb(31, 35, 41);"> : 这是最深层的“欺骗性”，决定了最终决赛的成绩。这意味着我的生成模型可能需要某种 </font>**<font style="color:rgb(31, 35, 41);">对抗性训练</font>**<font style="color:rgb(31, 35, 41);"> ，或者生成的语音在声学特征上要足够“像真实语音”，以骗过专门的 </font>**<font style="color:rgb(31, 35, 41);">语音反欺诈 (ASVspoof)</font>**<font style="color:rgb(31, 35, 41);"> 模型。</font>

# **<font style="color:rgb(31, 35, 41);">三、来仔细了解一下Baseline方案是如何实现解题的！</font>**
## <font style="color:rgb(31, 35, 41);">Baseline方案思路</font>
<font style="color:rgb(31, 35, 41);">F5-TTS 主要由两个模块组成：</font>

1. **<font style="color:rgb(31, 35, 41);">基于流匹配的 Mel 频谱图生成器</font>**<font style="color:rgb(31, 35, 41);"> : 这是一个基于 Transformer 架构的模型，带有 U-Net 风格的跳跃连接，负责将文本输入转换为 Mel 频谱图。</font>
2. **<font style="color:rgb(31, 35, 41);">声码器 (Vocoder)</font>**<font style="color:rgb(31, 35, 41);"> : 将生成的 Mel 频谱图转换成最终的音频波形。</font>

```plain
# Run with flags# Leave --ref_text "" will have ASR model transcribe (extra GPU memory usage)
f5-tts_infer-cli --model F5TTS_v1_Base \
--ref_audio "provide_prompt_wav_path_here.wav" \
--ref_text "The content, subtitle or transcription of reference audio." \
--gen_text "Some text you want TTS model generate for you."
```

## <font style="color:rgb(31, 35, 41);">Baseline核心逻辑</font>
<font style="color:rgb(31, 35, 41);">遍历所有任务，对每个任务使用一个预设的语音合成模型（F5-TTS）进行推理，将参考音频的风格迁移到目标文本上，并保存生成的语音文件。</font>

```plain
task = pd.read_csv("aigc_speech_generation_tasks/aigc_speech_generation_tasks.csv")

for row in task.iterrows():
    subprocess.check_output(
        f'f5-tts_infer-cli --model F5TTS_v1_Base --ref_audio "./aigc_speech_generation_tasks/{row[1].reference_speech}" --gen_text "{row[1].text}"',
        shell=True
    )
    shutil.move("tests/infer_cli_basic.wav", "result/" + str(row[1].utt) + ".wav")
```

# **<font style="color:rgb(31, 35, 41);">四、思考一下：如何上分？</font>**
<font style="color:rgb(31, 35, 41);">比赛不仅仅要求生成听起来不错的语音，更关键的是要生成能够 </font>**<font style="color:rgb(31, 35, 41);">欺骗现有反欺诈系统</font>**<font style="color:rgb(31, 35, 41);"> 的语音。这意味着，尽管高自然度、高可懂性和高说话人相似度至关重要，但它们最终都是 </font>**<font style="color:rgb(31, 35, 41);">达成目的的手段</font>**<font style="color:rgb(31, 35, 41);"> 。</font>

![](https://cdn.nlark.com/yuque/0/2025/png/39297154/1754831046948-8d58afd1-e920-4f07-8730-689473661c73.png)

<font style="color:rgb(31, 35, 41);">虽然通用 TTS 模型可以生成好的语音，但它可能仍会留下细微的伪影（例如，在相位、频谱纹理方面），这些伪影可能被专门的反欺诈模型检测到，即使人类不易察觉。这正是“攻击成功率”可能不足的地方。</font>

# **<font style="color:rgb(31, 35, 41);">五、下一个内容、我们将学习更多上分思路！</font>**
<font style="color:rgb(31, 35, 41);">你花了多少时间完成本篇内容呢？有哪些收获呢？可以在评论区分享分享~</font>

<font style="color:rgb(31, 35, 41);">然后、开始 </font>**<font style="color:rgb(31, 35, 41);">Task3：调整方案、进阶上分！（正在筹备中）</font>**<font style="color:rgb(31, 35, 41);"> 的学习吧！</font>

<font style="color:rgb(100, 106, 115);">参考思路：</font>

<font style="color:rgb(100, 106, 115);">将一个预训练的 </font>**<font style="color:rgb(100, 106, 115);">语音反欺诈（ASVspoof）检测器</font>**<font style="color:rgb(100, 106, 115);"> 作为生成器训练中的一个 </font>**<font style="color:rgb(100, 106, 115);">额外判别器</font>**<font style="color:rgb(100, 106, 115);"> 。</font>

<font style="color:rgb(100, 106, 115);">生成器不仅要骗过真实性判别器（GAN中的D），还要骗过 ASVspoof 判别器，使其将合成语音错误地判断为“真实”。</font>

  
 

