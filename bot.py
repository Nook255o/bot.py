import discord
from discord.ext import commands
from discord.ui import View, Select
import asyncio
from keep_alive import keep_alive

TOKEN = 'MTM1Mzk3MjI5NjE3MTM5MzE1NQ.GaYYZk.JLrt92elT-BtonJQOxGetkYgYp3HlMvNRXQROo'
GUILD_ID = 1336950984584335441
SHOP_CHANNEL_ID = 1399632842517905428
ADMIN_ROLE_ID = 1336951685880217650
CATEGORY_ID = 1354285091622486260

# สินค้าและสต็อก (key = ชื่อสินค้า, value = [ราคา, สต็อก])
PRODUCTS = {
    "สินค้า ไก่สปิงเกอร์": [39, 3],
    "สินค้า แรคคุณ": [200, 0],
    "สินค้า แมงปอ": [90, 2],
    "สินค้า ปลาหมึก": [75, 3],
    "สินค้า ทีเล็ก": [80, 2],
    "สินค้า ผึ่งดิสโก้": [180, 0],
    "สินค้า หูส้ม": [25, 4],
    "สินค้า จิ้งจอกฟ้า": [50, 4],
    "สินค้า kodama": [15, 48],
    "สินค้า แมวมูล": [25, 3],
}

# ลิงก์รูปภาพสินค้า
PRODUCT_IMAGES = {
    "สินค้า ไก่สปิงเกอร์": "https://media.discordapp.net/attachments/1349889157312286831/1399639285597995038/file_00000000b0306230accafabe63f5d9cd.png?ex=6889bb29&is=688869a9&hm=7666b06b39072af31c424bbd33cae14afcb2cef1d9964c041dd7843f20259e27&=&format=webp&quality=lossless&width=582&height=582",
    "สินค้า แรคคุณ": "https://media.discordapp.net/attachments/1336999472303177761/1399304873568374865/Raccon_Better_Quality.webp?ex=6889d537&is=688883b7&hm=2bcf90e1144dc0e747cb18c31196e7b22cfdc8fdcf202ba45ece4887a0523f22&=&format=webp",
    "สินค้า แมงปอ": "https://media.discordapp.net/attachments/1336999472303177761/1399711595323457666/file_000000004bcc61f59d1ba7942025b55d.png?ex=6889fe81&is=6888ad01&hm=4219f610482ffda9b1b9692c57c16a39bb4c571ecfaae1752c932d3d60a818e8&=&format=webp&quality=lossless&width=582&height=582",
    "สินค้า ปลาหมึก": "https://media.discordapp.net/attachments/1336999472303177761/1399307707592216628/1000.png?ex=6889d7db&is=6888865b&hm=bed9785896d266f708c30d17d09d99a1e23bc653bf5cfd0bd0b7d4200c1c2335&=&format=webp&quality=lossless&width=775&height=581",
    "สินค้า ทีเล็ก": "https://media.discordapp.net/attachments/1336999472303177761/1399325937731899392/image0.jpg?ex=6889e8d5&is=68889755&hm=53d6325cee27d7860120822c741111afd7984489048b23c1c643aa0f44f53098&=&format=webp",
    "สินค้า ผึ่งดิสโก้": "https://media.discordapp.net/attachments/1336999472303177761/1399307169479786558/1000.png?ex=6889d75b&is=688885db&hm=eb7ad5b3c9785387af34678a03f3e154a5aaca25fd1be65a7371b667ae9cdcf2&=&format=webp&quality=lossless&width=582&height=582",
    "สินค้า หูส้ม": "https://media.discordapp.net/attachments/1336999472303177761/1399307643151056919/latest.png?ex=6889d7cc&is=6888864c&hm=1ebd56b7a40080028c876e988e16ede0dbbeee1b6ec6c4176851d257293f64f5&=&format=webp&quality=lossless",
    "สินค้า จิ้งจอกฟ้า": "https://media.discordapp.net/attachments/1336999472303177761/1399713290111684618/CorruptedKitsune.png?ex=688a0015&is=6888ae95&hm=cd1aad62ab10820e91373ad6710490fbf76c08bbd262c9ee48546caadd8c4319&=&format=webp&quality=lossless",
    "สินค้า แมวมูล": "https://media.discordapp.net/attachments/1336999472303177761/1399309694710976552/1000.png?ex=6889d9b5&is=68888835&hm=2ecaad1d3a69ae6ac5ec0618e7e6d4638da79145def0b86b69f5d7327d9fe6ee&=&format=webp&quality=lossless&width=582&height=582",
}

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# SELECT สำหรับแสดงสินค้า
class ProductSelect(Select):
    def __init__(self):
        options = []
        for name, (price, stock) in PRODUCTS.items():
            if stock > 0:
                options.append(
                    discord.SelectOption(
                        label=name,
                        description=f"ราคา {price} บาท | คงเหลือ: {stock}",
                        value=f"{name}|{price}"
                    )
                )
        super().__init__(placeholder="🛍️ เลือกสินค้าที่คุณต้องการ...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        selected = self.values[0]
        label, price = selected.split("|")
        price = int(price)

        # ตรวจสอบสต็อกอีกครั้ง
        if PRODUCTS[label][1] <= 0:
            await interaction.followup.send("❌ สินค้าหมดสต็อก", ephemeral=True)
            return

        # ลดสต็อก
        PRODUCTS[label][1] -= 1

        # สร้างห้องส่วนตัว
        guild = bot.get_guild(GUILD_ID)
        category = discord.utils.get(guild.categories, id=CATEGORY_ID)
        admin_role = guild.get_role(ADMIN_ROLE_ID)

        if not all([guild, category, admin_role]):
            await interaction.followup.send("❌ เกิดข้อผิดพลาดกับข้อมูลเซิร์ฟเวอร์", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            admin_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        channel_name = f"🛒・{interaction.user.name}"
        private_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)

        await private_channel.send(f"✅ สร้างห้องสำหรับ <@{interaction.user.id}> เรียบร้อย กรุณารอสักครู่...")

        # ส่งปุ่มเสร็จสิ้นในห้องที่สร้าง พร้อม Embed ที่มีรูปสินค้า
        view = FinishView(original_interaction=interaction, private_channel=private_channel, admin_role_id=ADMIN_ROLE_ID)

        embed = discord.Embed(
            title="📦 รายละเอียดคำสั่งซื้อ",
            description=f"**สินค้า:** {label}\n**ราคา:** {price} บาท\n**ผู้ซื้อ:** <@{interaction.user.id}>\n <@&1336951685880217650>",
            color=discord.Color.green()
        )

        image_url = PRODUCT_IMAGES.get(label)
        if image_url:
            embed.set_image(url=image_url)

        await private_channel.send(embed=embed, view=view)

# VIEW สำหรับ Select Menu
class ProductSelectView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ProductSelect())

# VIEW ปุ่มเสร็จสิ้นและลิงก์เฉพาะแอดมิน
class FinishView(View):
    def __init__(self, original_interaction, private_channel, admin_role_id):
        super().__init__(timeout=None)
        self.original_interaction = original_interaction
        self.private_channel = private_channel
        self.admin_role_id = admin_role_id

    def is_admin(self, user):
        return self.admin_role_id in [role.id for role in user.roles]

    @discord.ui.button(label="✅ เสร็จสิ้น (แอดมินเท่านั้น)", style=discord.ButtonStyle.red)
    async def finish_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_admin(interaction.user):
            await interaction.response.send_message("❌ คุณไม่มีสิทธิ์กดปุ่มนี้ (เฉพาะแอดมิน)", ephemeral=True)
            return

        await interaction.response.send_message("✅ ปิดห้องเรียบร้อย", ephemeral=True)
        try:
            await self.private_channel.delete()
        except Exception:
            pass

        await update_shop_message()

    @discord.ui.button(label="💸 ชำระเงิน(แอดสนุกเกอร์)", style=discord.ButtonStyle.green)
    async def payment_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_admin(interaction.user):
            await interaction.response.send_message("❌ คุณไม่มีสิทธิ์กดปุ่มนี้ (เฉพาะแอดมิน)", ephemeral=True)
            return

        await interaction.response.send_message(
            content="**กรุณาเพื่อโอนเงิน**\n 💖✨ โอนเสร็จแล้วรบกวนแจ้งสลิปด้วยนะครับ\n 💌 พร้อมทั้งแจ้งชื่อในเกมมาด้วยนะครับ\n 🕹️ ขอบคุณมากครับ 🙏🌷",
            embed=discord.Embed().set_image(url="https://media.discordapp.net/attachments/1336999472303177761/1399726206634692648/Picsart_25-07-16_04-19-09-531.jpg?ex=688a0c1d&is=6888ba9d&hm=f1b00f447da0c60c823a4dc78bcd1b426e80ae9752602ed992ba52d5700f5660&=&format=webp&width=582&height=582")
        )

    @discord.ui.button(label="💸 ชำระเงิน(แอดมาย)", style=discord.ButtonStyle.green)
    async def bank_transfer_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_admin(interaction.user):
            await interaction.response.send_message("❌ คุณไม่มีสิทธิ์กดปุ่มนี้ (เฉพาะแอดมิน)", ephemeral=True)
            return

        await interaction.response.send_message(
            content="**กรุณาเพื่อโอนเงิน**\n 💖✨ โอนเสร็จแล้วรบกวนแจ้งสลิปด้วยนะครับ\n 💌 พร้อมทั้งแจ้งชื่อในเกมมาด้วยนะครับ\n 🕹️ ขอบคุณมากครับ 🙏🌷",
            embed=discord.Embed().set_image(url="https://media.discordapp.net/attachments/1336999472303177761/1399729881394315324/40a74a73ba05ba8ad3ad50c3c0bc0fec.jpg?ex=688a0f89&is=6888be09&hm=46baaa46bd83fdfd136ef8d9e3aaf2adea5680497ca871deca7bb57b18ff9255&=&format=webp&width=582&height=582")
        )

    @discord.ui.button(label="💸 ชำระเงิน(แอดพลอย)", style=discord.ButtonStyle.green)
    async def promptpay_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_admin(interaction.user):
            await interaction.response.send_message("❌ คุณไม่มีสิทธิ์กดปุ่มนี้ (เฉพาะแอดมิน)", ephemeral=True)
            return

        await interaction.response.send_message(
            content="**กรุณาเพื่อโอนเงิน**\n 💖✨ โอนเสร็จแล้วรบกวนแจ้งสลิปด้วยนะครับ\n 💌 พร้อมทั้งแจ้งชื่อในเกมมาด้วยนะครับ\n 🕹️ ขอบคุณมากครับ 🙏🌷",
            embed=discord.Embed().set_image(url="https://media.discordapp.net/attachments/1336999472303177761/1399727544961601566/0F053F0A-5D32-4F75-978E-4AF8D4C23D23.jpg?ex=688a0d5c&is=6888bbdc&hm=d711977324cfd816e98fc01b58eca3036d956d495bc498a6e2fcaa28f0adf508&=&format=webp&width=563&height=582")
        )

    @discord.ui.button(label="🌐 ส่งลิงก์เซิร์ฟเวอร์", style=discord.ButtonStyle.blurple)
    async def link_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_admin(interaction.user):
            await interaction.response.send_message("❌ คุณไม่มีสิทธิ์กดปุ่มนี้ (เฉพาะแอดมิน)", ephemeral=True)
            return

        embed = discord.Embed(
            title="🌐 ลิงก์เซิร์ฟเวอร์",
            description="เข้าร่วมเซิร์ฟเวอร์ผ่านลิงก์นี้:\n https://www.roblox.com/share?code=2d818aef5d7e084b93ccfd6fc4f1e385&type=Server",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=False)

# ฟังก์ชันอัปเดต Embed ใน SHOP
async def update_shop_message():
    channel = bot.get_channel(SHOP_CHANNEL_ID)
    if not channel:
        return

    await channel.purge(limit=10)

    embed = discord.Embed(
        title="🎉 ร้านค้า MYMELODYSHOP",
        description="เลือกสินค้าที่คุณต้องการจากแถบด้านล่าง แล้วรอระบบสร้างห้องอัตโนมัติ 💖",
        color=discord.Color.pink()
    )

    for name, (price, stock) in PRODUCTS.items():
        status = f"🟢 คงเหลือ: {stock}" if stock > 0 else "🔴 หมดสต็อก"
        embed.add_field(name=name, value=f"💸 ราคา: {price} บาท\n{status}", inline=True)

    await channel.send(embed=embed, view=ProductSelectView())

@bot.event
async def on_ready():
    print(f'✅ Bot พร้อมใช้งานแล้ว: {bot.user.name}')
    await update_shop_message()

keep_alive()
bot.run(TOKEN)