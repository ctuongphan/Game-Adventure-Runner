import pygame
from pygame import mixer
import os
import random
import csv
import button

mixer.init()
pygame.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Adventure Runner')

#set framerate
clock = pygame.time.Clock()
FPS = 60

#define game variables
GRAVITY = 0.75
SCROLL_THRESH = 400
ROWS = 16
COLS = 120
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 27
MAX_LEVELS = 2
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False
menu_game = False
Vel_YY = -14

scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1

#define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False


#load music and sounds
jump_fx = pygame.mixer.Sound('PROJECT/audio/jump.wav')
jump_fx.set_volume(0.05)
shot_fx = pygame.mixer.Sound('PROJECT/audio/shot.wav')
shot_fx.set_volume(0.05)
grenade_fx = pygame.mixer.Sound('PROJECT/audio/grenade.wav')
grenade_fx.set_volume(0.05)


#load images
#button images
start_img = pygame.image.load('PROJECT/IMG/start_btn.png').convert_alpha()
exit_img = pygame.image.load('PROJECT/IMG/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('PROJECT/IMG/restart_btn.png').convert_alpha()
menu_img = pygame.image.load('PROJECT/IMG/menu.jpg').convert_alpha()
pause_img = pygame.image.load('PROJECT/IMG/pausen.png').convert_alpha()
#background
sky_img = pygame.image.load('PROJECT/IMG/Background/bg1.png').convert_alpha()
#store tiles in a list
img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f'PROJECT/IMG/Tile/{x}.png')
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img_list.append(img)
#bullet
bullet_img = pygame.image.load('PROJECT/IMG/icons/bullet.png').convert_alpha()

#pick up boxes
health_box_img = pygame.image.load('PROJECT/IMG/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('PROJECT/IMG/icons/ammo_box.png').convert_alpha()
Shoe_box_img = pygame.image.load('PROJECT/IMG/icons/21.png').convert_alpha()

item_boxes = {
	'Health'	: health_box_img,
	'Ammo'		: ammo_box_img,
	'Shoe'		: Shoe_box_img
}


#define colours
#BG = (144, 201, 120)
BG = (255, 193, 193)
RED = (255, 0, 0)
RED1 = (205, 85, 85)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GREEN1 = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

#define font
font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, text_col, x, y):
	"""
	Input:
text (str): Chuỗi văn bản cần vẽ.
font (pygame.font.Font): Đối tượng font được sử dụng để vẽ văn bản.
text_col (tuple): Màu của văn bản dưới dạng một bộ ba số nguyên (R, G, B).
x (int): Tọa độ x của vị trí xuất phát của văn bản trên màn hình.
y (int): Tọa độ y của vị trí xuất phát của văn bản trên màn hình.
	Output:
Phương thức này vẽ một chuỗi văn bản được cung cấp lên màn hình tại vị trí xác định,
sử dụng font và màu sắc được chỉ định.
	"""
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


def draw_bg():
	"""
	Output:
 Hàm này sẽ vẽ nền của trò chơi và các lớp nền phía sau nhân vật.
	"""
	screen.fill(BG)
	width = sky_img.get_width()
	for x in range(5): 
		screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))


#create buttons
#make a button list
button_list = []
button_col = 0
button_row = 0
for i in range(len(img_list)):
    tile_button = button.Button(SCREEN_WIDTH + (75 * button_col) + 50, 75 * button_row + 50, img_list[i], 1)
    button_list.append(tile_button)
    button_col += 1
    if button_col == 3:
        button_row += 1
        button_col = 0

#function to reset level
def reset_level():
	"""
 	Output:
 Phương thức này xóa tất cả các đối tượng khỏi các nhóm như nhóm quái vật, nhóm đạn, nhóm hộp vật phẩm, vv.
Sau đó, nó tạo ra một danh sách 2D trống với các giá trị âm (-1) cho mỗi ô, để đại diện cho màn hình trống.
Đây là một phần của quy trình để chuẩn bị một cấp độ mới của trò chơi.
	"""
	Monster_group.empty()
	bullet_group.empty()
	item_box_group.empty()
	decoration_group.empty()
	water_group.empty()
	exit_group.empty()

	#create empty tile list
	data = []
	for row in range(ROWS):
		r = [-1] * COLS
		data.append(r)

	return data


"""
    Đại diện cho một nhân vật trong trò chơi.

    Tham số:
        char_type (str): Loại nhân vật ('player' hoặc 'Monster').
        x (int): Tọa độ X của vị trí bắt đầu của nhân vật.
        y (int): Tọa độ Y của vị trí bắt đầu của nhân vật.
        scale (float): Hệ số thu phóng cho kích thước của nhân vật.
        speed (int): Tốc độ di chuyển của nhân vật.
        ammo (int): Số lượng đạn của nhân vật.
        grenades (int): Số lượng lựu đạn của nhân vật.
        index (int, tùy chọn): Chỉ số của nhân vật, mặc định là 1.

    Thuộc tính:
        alive (bool): Cho biết liệu nhân vật còn sống hay không.
        char_type (str): Loại nhân vật ('player' hoặc 'Monster').
        speed (int): Tốc độ di chuyển của nhân vật.
        ammo (int): Số lượng đạn của nhân vật.
        start_ammo (int): Số đạn ban đầu.
        shoot_cooldown (int): Thời gian nghỉ sau mỗi lần bắn.
        grenades (int): Số lượng lựu đạn của nhân vật.
        health (int): Sức khỏe hiện tại của nhân vật.
        max_health (int): Sức khỏe tối đa của nhân vật.
        direction (int): Hướng mà nhân vật đang nhìn ( -1 cho trái, 1 cho phải).
        vel_y (int): Vận tốc theo chiều dọc của nhân vật.
        jump (bool): Cho biết liệu nhân vật đang nhảy hay không.
        in_air (bool): Cho biết liệu nhân vật có đang ở trạng thái nảy hay không.
        flip (bool): Cho biết liệu hình ảnh của nhân vật có bị lật ngược hay không.
        animation_list (list): Danh sách chứa các khung hình của hoạt hình của nhân vật.
        frame_index (int): Chỉ số của khung hình hiện tại trong danh sách hoạt hình.
        action (int): Hành động hiện tại của nhân vật (0 cho đứng yên, 1 cho chạy, 2 cho nhảy, 3 cho chết).
        update_time (int): Thời gian cập nhật hoạt hình lần cuối.
        move_counter (int): Bộ đếm cho việc di chuyển của nhân vật.
        vision (pygame.Rect): Hình chữ nhật đại diện cho phạm vi tầm nhìn của nhân vật.
        idling (bool): Cho biết liệu nhân vật có đang đứng yên hay không.
        idling_counter (int): Bộ đếm cho thời gian nhân vật đứng yên.
        index (int): Chỉ số của nhân vật.
        vel_yy (int): Bộ điều chỉnh vận tốc theo chiều dọc cho việc nhảy.

    Phương thức:
        update(self): Cập nhật trạng thái và hoạt hình của nhân vật.
        move(self, moving_left, moving_right): Di chuyển nhân vật theo chiều ngang và xử lý việc nhảy.
        shoot(self): Bắn đạn nếu điều kiện đủ.
        ai(self): Xử lý hành vi trí tuệ nhân tạo cho nhân vật.
        update_animation(self): Cập nhật các khung hình hoạt hình của nhân vật.
        update_action(self, new_action): Cập nhật hành động của nhân vật.
        check_alive(self): Kiểm tra xem nhân vật còn sống hay không.
        draw(self): Vẽ nhân vật lên màn hình.
"""
class Princess(pygame.sprite.Sprite):
	def __init__(self, char_type, x, y, scale, speed, ammo, index = 1):
		"""
		Khởi tạo một nhân vật mới.

		Tham số:
		- char_type: Loại nhân vật (vd: 'Player', 'Enemy').
		- x: Tọa độ x ban đầu của nhân vật trên màn hình.
		- y: Tọa độ y ban đầu của nhân vật trên màn hình.
		- scale: Tỉ lệ để co giãn hình ảnh của nhân vật.
		- speed: Tốc độ di chuyển của nhân vật.
		- ammo: Số lượng đạn ban đầu mà nhân vật có.
		- index: Chỉ số để phân biệt giữa các nhân vật cùng loại.

		Trả về:
		Không có giá trị trả về.
		"""
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.char_type = char_type
		self.speed = speed
		self.ammo = ammo
		self.start_ammo = ammo
		self.shoot_cooldown = 0
		self.health = 100
		self.max_health = self.health
		self.direction = 1
		self.vel_y = 0
		self.jump = False
		self.in_air = True
		self.flip = False
		self.animation_list = []
		self.frame_index = 0
		self.action = 0
		self.update_time = pygame.time.get_ticks()
		#ai specific variables
		self.move_counter = 0
		self.vision = pygame.Rect(0, 0, 150, 20)
		self.idling = False
		self.idling_counter = 0
		self.index = index
		self.vel_yy =0
		
		#load all images for the players
		animation_types = [ 'Run', 'Jump', 'Walk','Die']
		for animation in animation_types:
			#reset temporary list of images
			temp_list = []
			#count number of files in the folder
			num_of_frames = len(os.listdir(f'PROJECT/IMG/{self.char_type}{self.index}/{animation}'))
			for i in range(num_of_frames):
				img = pygame.image.load(f'PROJECT/IMG/{self.char_type}{self.index}/{animation}/{i}.png').convert_alpha()
				img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
				temp_list.append(img)
			self.animation_list.append(temp_list)

		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()

     
	def update(self):
		"""
		Input: Không có.
		Output:  Cập nhật trạng thái và hoạt hình của nhân vật.
		"""
		self.update_animation()
		self.check_alive()
		#update cooldown
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1


	def move(self, moving_left, moving_right):
		"""
		Xử lý việc di chuyển của nhân vật.

		Input:
		moving_left: True nếu nhân vật đang di chuyển sang trái, False nếu không.
		moving_right: True nếu nhân vật đang di chuyển sang phải, False nếu không.

		Output:
		screen_scroll: Sự thay đổi tọa độ của màn hình, để cuộn màn hình khi nhân vật tiến gần biên.
		level_complete: True nếu nhân vật chạm vào điểm kết thúc cấp độ, False nếu không.
		"""
		
		#reset movement variables
		screen_scroll = 0
		Vel_YY= -14
		dx = 0
		dy = 0
		center_x = SCREEN_WIDTH // 2
  
		#assign movement variables if moving left or right
		if moving_left:
			dx = -self.speed
			self.flip = True
			self.direction = -1
		if moving_right:
			dx = self.speed
			self.flip = False
			self.direction = 1

		#jump
		if self.jump == True and self.in_air == False:
			self.vel_y = -14 - self.vel_yy
			self.jump = False
			self.in_air = True

		#apply gravity
		self.vel_y += GRAVITY
		if self.vel_y > 10:
			self.vel_y
		dy += self.vel_y

		#check for collision
		for tile in world.obstacle_list:
			#check collision in the x direction
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				dx = 0
				#if the ai has hit a wall then make it turn around
				if self.char_type == 'Monster':
					self.direction *= -1
					self.move_counter = 0
			#check for collision in the y direction
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				#check if below the ground, i.e. jumping
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				#check if above the ground, i.e. falling
				elif self.vel_y >= 0:
					self.vel_y = 0
					self.in_air = False
					dy = tile[1].top - self.rect.bottom


		#check for collision with water
		if pygame.sprite.spritecollide(self, water_group, False):
			self.health = 0

		#check for collision with exit
		level_complete = False
		if pygame.sprite.spritecollide(self, exit_group, False):
			level_complete = True

		#check if fallen off the map
		if self.rect.bottom > SCREEN_HEIGHT:
			self.health = 0


		#check if going off the edges of the screen
		if self.char_type == 'player':
			if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
				dx = 0
		
			
		#update rectangle position
		self.rect.x += dx
		self.rect.y += dy

		#update scroll based on player position
		if self.char_type == 'player':
#   and (moving_left or moving_right):
			if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
				or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
				self.rect.x -= dx
				screen_scroll -= dx
   
			# if self.rect.centerx >= center_x:
			# 	screen_scroll -= self.speed
			# 	self.rect.x -= self.speed  # Di chuyển nhân vật ngược lại để giữ nguyên vị trí giữa màn hình
			# else:
			# 	screen_scroll = 0

			
		return screen_scroll, level_complete



	def shoot(self):
		"""
	Output:

	Nếu shoot_cooldown bằng 0 và ammo lớn hơn 0:
	Tạo một đối tượng đạn mới tại vị trí centerx của nhân vật với khoảng cách dọc bằng 0.75 chiều rộng của nhân vật (0.75 * self.rect.size[0]) và vị trí centery của nhân vật.
	Thêm đối tượng đạn vào nhóm đạn (bullet_group).
	Giảm ammo đi 1.
	Phát âm thanh khi bắn đạn (shot_fx).
		"""
		if self.shoot_cooldown == 0 and self.ammo > 0:
			self.shoot_cooldown = 20
			bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
			bullet_group.add(bullet)
			#reduce ammo
			self.ammo -= 1
			shot_fx.play()


	def ai(self):
		"""
	Input:
player: Đối tượng người chơi.
screen_scroll: Sự thay đổi vị trí của màn hình.

	Output:
Hàm này sẽ thực hiện các hành động sau:
Kiểm tra xem Monster và người chơi có còn sống không.
Nếu Monster không đang trong trạng thái đứng yên và số ngẫu nhiên trong khoảng từ 1 đến 200 là 1, nó sẽ cập nhật hành động thành trạng thái đứng yên và bắt đầu tính ngược thời gian đứng yên.
Kiểm tra xem Monster có gần người chơi không bằng cách kiểm tra xem vùng nhìn của nó (vision) có chồng lấn với vùng của người chơi không. Nếu có, nó sẽ ngừng chạy và nhìn về phía người chơi, sau đó bắn đạn.
Nếu không, nó sẽ tiếp tục di chuyển:
Nếu đang trong trạng thái đứng yên, nó sẽ xác định hướng di chuyển và thực hiện di chuyển.
Nếu di chuyển sang trái hoặc phải, nó sẽ cập nhật hành động thành trạng thái chạy.
Nếu không đứng yên, nó sẽ đếm ngược thời gian đứng yên và khi hết thời gian, nó sẽ trở lại trạng thái di chuyển.
Cuối cùng, vị trí của Monster sẽ được cập nhật dựa trên screen_scroll để đảm bảo nó di chuyển cùng với màn hình.
		"""
		if self.alive and player.alive:
			if self.idling == False and random.randint(1, 200) == 1:
				self.update_action(0)#0: idle
				self.idling = True
				self.idling_counter = 50
			#check if the ai in near the player
			if self.vision.colliderect(player.rect):
				#stop running and face the player
				self.update_action(0)#0: idle
				#shoot
				self.shoot()
			else:
				if self.idling == False:
					if self.direction == 1:
						ai_moving_right = True
					else:
						ai_moving_right = False
					ai_moving_left = not ai_moving_right
					self.move(ai_moving_left, ai_moving_right)
					self.update_action(1)#1: run
					self.move_counter += 1
					#update ai vision as the Monster moves
					self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

					if self.move_counter > TILE_SIZE:
						self.direction *= -1
						self.move_counter *= -1
				else:
					self.idling_counter -= 1
					if self.idling_counter <= 0:
						self.idling = False

		#scroll
		self.rect.x += screen_scroll


	def update_animation(self):
		"""
	Output:
Cập nhật self.image thành frame tiếp theo của animation.
Nếu đủ thời gian đã trôi qua kể từ lần cập nhật animation trước đó, cập nhật self.frame_index sang frame tiếp theo.
Nếu đã hiển thị hết tất cả các frame của animation, reset self.frame_index về 0 hoặc frame cuối cùng tùy thuộc vào hành động hiện tại của nhân vật.
		"""
		#update animation
		ANIMATION_COOLDOWN = 100
		#update image depending on current frame
		self.image = self.animation_list[self.action][self.frame_index]
		#check if enough time has passed since the last update
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		#if the animation has run out the reset back to the start
		if self.frame_index >= len(self.animation_list[self.action]):
			if self.action == 3:
				self.frame_index = len(self.animation_list[self.action]) - 1
			else:
				self.frame_index = 0



	def update_action(self, new_action):
		"""
  	Input:
new_action: Một giá trị mới cho hành động của nhân vật.
	Output:
Nếu new_action khác với hành động hiện tại (self.action), hàm sẽ cập nhật self.action với giá trị mới và đặt self.frame_index về 0 để bắt đầu chạy animation từ đầu.
Hàm cũng cập nhật thời gian cập nhật (self.update_time) bằng thời gian hiện tại.
		"""
		#check if the new action is different to the previous one
		if new_action != self.action:
			self.action = new_action
			#update the animation settings
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()



	def check_alive(self):
		"""
	Output:
Hàm này kiểm tra xem nhân vật có còn số máu lớn hơn 0 hay không. Nếu không, nó sẽ đặt số máu của nhân vật về 0, làm chậm tốc độ của nhân vật, đặt cờ alive của nhân vật thành False (đánh dấu nhân vật đã chết), và cập nhật hành động của nhân vật thành hành động 3 (die).
		"""
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.alive = False
			self.update_action(3)


	def draw(self):
		"""
	Output:
Vẽ hình ảnh của Princess lên màn hình với việc lật theo chiều ngang (nếu được yêu cầu).
		"""
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


"""
    Đại diện cho một vùng nước trong trò chơi.

    Tham số:
        img (pygame.Surface): Hình ảnh đại diện cho vùng nước.
        x (int): Tọa độ X của vị trí của vùng nước.
        y (int): Tọa độ Y của vị trí của vùng nước.

    Thuộc tính:
        image (pygame.Surface): Hình ảnh của vùng nước.
        rect (pygame.Rect): Hình chữ nhật giới hạn vùng nước trên màn hình.

    Phương thức:
        update(self): Cập nhật vị trí của vùng nước dựa trên sự cuộn màn hình.
"""

class Water(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		"""
  	Input:
        img (pygame.Surface): Hình ảnh của sprite.
        x (int): Tọa độ x của sprite trên màn hình.
        y (int): Tọa độ y của sprite trên màn hình.

    Output:
		Khởi tạo một đối tượng sprite mới.
		Đối tượng sprite này được sử dụng để hiển thị một hình ảnh cụ thể trên màn hình.
		"""
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		"""
	Output:
Hàm này chỉ thay đổi thuộc tính self.rect.x của đối tượng. Điều này dẫn đến di chuyển của đối tượng theo hướng và khoảng cách được chỉ định bởi screen_scroll.
		"""
		self.rect.x += screen_scroll

"""
    Đại diện cho thế giới trong trò chơi.

    Thuộc tính:
        obstacle_list (list): Danh sách chứa các vật cản trong thế giới.

    Phương thức:
        __init__(self): Khởi tạo một thế giới mới.
        process_data(self, data, index): Xử lý dữ liệu cấp độ để tạo ra các đối tượng trong thế giới.
        draw(self): Vẽ các đối tượng trong thế giới lên màn hình.
"""
class World():
	def __init__(self):
		"""
	Output:
		Khởi tạo một thế giới mới.
		"""
		self.obstacle_list = []
  
	def process_data(self, data, index):
		"""
	Input:
data: Mảng 2 chiều chứa dữ liệu của cấp độ trò chơi, trong đó mỗi phần tử đại diện cho một ô trong bản đồ.
index: Chỉ mục của nhân vật (player).
	Output:
player: Đối tượng Princess đại diện cho nhân vật player.
health_bar: Đối tượng HealthBar đại diện cho thanh máu của nhân vật player.
		"""
		self.level_length = len(data[0])
		#iterate through each value in level data file
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >= 0:
					img = img_list[tile]
					img_rect = img.get_rect()
					img_rect.x = x * TILE_SIZE
					img_rect.y = y * TILE_SIZE
					tile_data = (img, img_rect)
					if (tile >= 0 and tile <= 8) or (tile >=11 and tile <=14) or  tile == 18 or (tile>=22 and tile<=26):
						self.obstacle_list.append(tile_data)
					elif tile >= 9 and tile <= 10:
						water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
						water_group.add(water)
					elif tile >= 11 and tile <= 14:
						decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
						decoration_group.add(decoration)
					elif tile == 15:#create player
						# player = Princess('player', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5,index)
						player = Princess('player', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20,index)
						health_bar = HealthBar(10, 10, player.health, player.health)
					elif tile == 16:#create enemies
						# Monster = Princess('Monster', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0,1)	
						Monster = Princess('Monster', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 1)
						Monster_group.add(Monster)
					elif tile == 17:#create ammo box
						item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE, 35, 35)
						item_box_group.add(item_box)
					elif tile == 19:#create health box
						item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE, 35, 35)
						item_box_group.add(item_box)
					elif tile == 20:#create exit
						exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
						exit_group.add(exit)
					elif tile == 21:#create exit
						item_box = ItemBox('Shoe', x * TILE_SIZE, y * TILE_SIZE, 35, 35)
						item_box_group.add(item_box)

		return player, health_bar


	def draw(self):
		"""
	Output:
Hàm này chỉ thực hiện vẽ lại các ô cản trong trò chơi (tiles) sau khi đã được dịch chuyển dựa trên sự thay đổi của màn hình (screen_scroll). Cụ thể, nó di chuyển các ô cản theo hướng đối lập với hướng di chuyển của màn hình, sau đó vẽ chúng lên màn hình.
		"""
		for tile in self.obstacle_list:
			tile[1][0] += screen_scroll
			screen.blit(tile[0], tile[1])

"""
    Đại diện cho một đối tượng trang trí trong trò chơi.

    Tham số:
        img (pygame.Surface): Hình ảnh đại diện cho đối tượng trang trí.
        x (int): Tọa độ X của vị trí của đối tượng trang trí.
        y (int): Tọa độ Y của vị trí của đối tượng trang trí.

    Thuộc tính:
        image (pygame.Surface): Hình ảnh của đối tượng trang trí.
        rect (pygame.Rect): Hình chữ nhật giới hạn đối tượng trang trí trên màn hình.

    Phương thức:
        update(self): Cập nhật vị trí của đối tượng trang trí dựa trên sự cuộn màn hình.
"""

class Decoration(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		"""
	Input:
img: Hình ảnh của sprite.
x: Tọa độ x của sprite.
y: Tọa độ y của sprite.
	Output:
Hàm chỉ khởi tạo các thuộc tính của đối tượng.
		"""
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		"""
	Output:
Cập nhật vị trí x mới của đối tượng sau khi dịch chuyển theo screen_scroll.
		"""
		self.rect.x += screen_scroll


"""
    Đại diện cho một đối tượng cổng thoát trong trò chơi.

    Tham số:
        img (pygame.Surface): Hình ảnh đại diện cho đối tượng cổng thoát.
        x (int): Tọa độ X của vị trí của đối tượng cổng thoát.
        y (int): Tọa độ Y của vị trí của đối tượng cổng thoát.

    Thuộc tính:
        image (pygame.Surface): Hình ảnh của đối tượng cổng thoát.
        rect (pygame.Rect): Hình chữ nhật giới hạn đối tượng cổng thoát trên màn hình.

    Phương thức:
        update(self): Cập nhật vị trí của đối tượng cổng thoát dựa trên sự cuộn màn hình.
"""

class Exit(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		"""
	Input:
img: Một hình ảnh của sprite.
x: Tọa độ x của sprite.
y: Tọa độ y của sprite.
	Output:
Hàm này khởi tạo một sprite với hình ảnh và tọa độ đã cho.
		"""
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		"""
	Output:
Hàm này chỉ thay đổi thuộc tính rect.x của đối tượng Sprite, điều chỉnh vị trí của nó dựa trên sự dịch chuyển của màn hình (screen_scroll).
		"""
		self.rect.x += screen_scroll

"""
    Đại diện cho một hộp vật phẩm trong trò chơi.

    Tham số:
        item_type (str): Loại vật phẩm trong hộp ('Health', 'Ammo', 'Grenade', 'Shoe').
        x (int): Tọa độ X của vị trí của hộp vật phẩm.
        y (int): Tọa độ Y của vị trí của hộp vật phẩm.

    Thuộc tính:
        item_type (str): Loại vật phẩm trong hộp ('Health', 'Ammo', 'Grenade', 'Shoe').
        image (pygame.Surface): Hình ảnh của hộp vật phẩm.
        rect (pygame.Rect): Hình chữ nhật giới hạn hộp vật phẩm trên màn hình.

    Phương thức:
        update(self): Cập nhật vị trí của hộp vật phẩm dựa trên sự cuộn màn hình và xử lý khi người chơi nhận được hộp vật phẩm.
"""

class ItemBox(pygame.sprite.Sprite):
	def __init__(self, item_type, x, y, width, height):
		"""
	Input:
item_type: Loại của hộp vật phẩm.
x: Tọa độ x của hộp vật phẩm.
y: Tọa độ y của hộp vật phẩm.
width: Chiều rộng của hộp vật phẩm.
height: Chiều cao của hộp vật phẩm.
	Output:
Khởi tạo một đối tượng vật phẩm với các thuộc tính sau:
item_type: Loại của hộp vật phẩm.
image: Hình ảnh của hộp vật phẩm đã được chuyển đổi kích thước thành (width, height).
rect: Hình chữ nhật giới hạn của hộp vật phẩm, có tọa độ (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height())) cho điểm trung tâm trên cùng.
		"""
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		# self.image = item_boxes[self.item_type]
		self.image = pygame.transform.scale(item_boxes[self.item_type], (width, height))
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


	def update(self):
		"""
	Output:
Nếu người chơi va chạm với vật phẩm, vật phẩm sẽ kiểm tra loại và thực hiện hành động tương ứng:
Nếu loại là 'Health', sức khỏe của người chơi tăng thêm 25 điểm. Nếu sức khỏe vượt quá giới hạn tối đa, sẽ được cắt ngắn để không vượt quá giới hạn đó.
Nếu loại là 'Ammo', số lượng đạn của người chơi tăng thêm 15 viên.
Nếu loại là 'Shoe', tốc độ rơi của người chơi tăng lên 4 pixel mỗi frame.
Hộp sẽ bị xóa sau khi được chọn.
		"""
		#scroll
		self.rect.x += screen_scroll
		#check if the player has picked up the box
		if pygame.sprite.collide_rect(self, player):
			#check what kind of box it was
			if self.item_type == 'Health':
				player.health += 25
				if player.health > player.max_health:
					player.health = player.max_health
			elif self.item_type == 'Ammo':
				player.ammo += 15
			# elif self.item_type == 'Grenade':
			# 	player.grenades += 3
			elif self.item_type == 'Shoe':
				#delete the item box
				player.vel_yy = 4
				
			self.kill()

"""
    Đại diện cho thanh máu trong trò chơi.

    Tham số:
        x (int): Tọa độ X của thanh máu trên màn hình.
        y (int): Tọa độ Y của thanh máu trên màn hình.
        health (int): Sức khỏe hiện tại.
        max_health (int): Sức khỏe tối đa.

    Phương thức:
        draw(self, health): Vẽ thanh máu trên màn hình với sức khỏe mới cập nhật.
"""

class HealthBar():
	def __init__(self, x, y, health, max_health):
		"""
		Input:
x: Tọa độ x của thanh máu trên màn hình.
y: Tọa độ y của thanh máu trên màn hình.
health: Số lượng máu hiện tại của đối tượng.
max_health: Số lượng máu tối đa của đối tượng.
	Output:
Hàm này chỉ khởi tạo các thuộc tính của thanh máu cho đối tượng.
		"""
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health

	def draw(self, health):
		"""
	Input:
health: Giá trị hiện tại của sức khỏe của đối tượng.
	Output:
Vẽ thanh máu trên màn hình với sức khỏe mới được cập nhật.
Giải thích:
Hàm draw này nhận giá trị sức khỏe hiện tại của đối tượng và vẽ thanh máu tương ứng trên màn hình.
Cập nhật giá trị sức khỏe mới cho đối tượng.
Tính tỷ lệ sức khỏe so với sức khỏe tối đa.
Vẽ một hình chữ nhật màu đen (viền) có kích thước lớn hơn so với phần hiển thị sức khỏe.
Vẽ một hình chữ nhật màu đỏ (nền) biểu thị phần sức khỏe còn lại.
Vẽ một hình chữ nhật màu xanh lá cây (nội dung) biểu thị phần sức khỏe hiện tại dựa trên tỷ lệ tính toán.
		"""
		#update with new health
		self.health = health
		#calculate health ratio
		ratio = self.health / self.max_health
		# pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
		pygame.draw.rect(screen, BLACK, (self.x - 1, self.y - 1, 152, 22))
		pygame.draw.rect(screen, RED1, (self.x, self.y, 150, 20))
		pygame.draw.rect(screen, GREEN1, (self.x, self.y, 150 * ratio, 20))

"""
    Đại diện cho một viên đạn trong trò chơi.

    Tham số:
        x (int): Tọa độ X ban đầu của viên đạn.
        y (int): Tọa độ Y ban đầu của viên đạn.
        direction (int): Hướng di chuyển của viên đạn (-1 hoặc 1).

    Thuộc tính:
        speed (int): Tốc độ di chuyển của viên đạn.
        image (pygame.Surface): Hình ảnh của viên đạn.
        rect (pygame.Rect): Hình chữ nhật giới hạn viên đạn trên màn hình.
        direction (int): Hướng di chuyển của viên đạn (-1 hoặc 1).

    Phương thức:
        update(self): Cập nhật vị trí của viên đạn và xử lý va chạm với các đối tượng trong trò chơi.
"""

class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		"""
	Input:
x: Tọa độ x ban đầu của viên đạn.
y: Tọa độ y ban đầu của viên đạn.
direction: Hướng di chuyển của viên đạn (1: sang phải, -1: sang trái).
	Output:
Hàm này chỉ khởi tạo một đối tượng viên đạn với các thuộc tính như tốc độ, hình ảnh, vị trí ban đầu và hướng di chuyển.
		"""
		pygame.sprite.Sprite.__init__(self)
		self.speed = 10
		self.image = bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction

	def update(self):
		"""
	Output:
Cập nhật vị trí của viên đạn.
Kiểm tra va chạm với các chướng ngại vật trong thế giới trò chơi và diệt viên đạn nếu có va chạm.
Kiểm tra va chạm với người chơi và quái vật, giảm sức khỏe của họ tương ứng nếu có va chạm và diệt viên đạn.
		"""
		#move bullet
		self.rect.x += (self.direction * self.speed) + screen_scroll
		#check if bullet has gone off screen
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill()
		#check for collision with level
		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect):
				self.kill()

		#check collision with characters
		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				player.health -= 5
				self.kill()
		for Monster in Monster_group:
			if pygame.sprite.spritecollide(Monster, bullet_group, False):
				if Monster.alive:
					Monster.health -= 25
					self.kill()


"""
    Đại diện cho hiệu ứng làm mờ màn hình trong trò chơi.

    Tham số:
        direction (int): Hướng của hiệu ứng làm mờ màn hình (1 hoặc 2).
        colour (tuple): Màu của hiệu ứng làm mờ màn hình (dạng (R, G, B)).
        speed (int): Tốc độ của hiệu ứng làm mờ màn hình.

    Thuộc tính:
        direction (int): Hướng của hiệu ứng làm mờ màn hình (1 hoặc 2).
        colour (tuple): Màu của hiệu ứng làm mờ màn hình (dạng (R, G, B)).
        speed (int): Tốc độ của hiệu ứng làm mờ màn hình.
        fade_counter (int): Bộ đếm để điều chỉnh tốc độ và kích thước của hiệu ứng làm mờ.

    Phương thức:
        fade(self): Thực hiện hiệu ứng làm mờ màn hình và trả về True nếu hiệu ứng đã hoàn thành.
"""

class ScreenFade():
	def __init__(self, direction, colour, speed):
		"""
		Input:
direction: Hướng di chuyển của hiệu ứng (ví dụ: "left", "right", "up", "down").
colour: Màu sắc của hiệu ứng.
speed: Tốc độ di chuyển của hiệu ứng.
		Output:
Hàm này chỉ khởi tạo các thuộc tính của đối tượng hiệu ứng.
		"""
		self.direction = direction
		self.colour = colour
		self.speed = speed
		self.fade_counter = 0


	def fade(self):
		"""
		Output:
fade_complete: Trạng thái của quá trình fade (True nếu hoàn thành, False nếu chưa hoàn thành).
		"""
		fade_complete = False
		self.fade_counter += self.speed
		if self.direction == 1:#whole screen fade
			pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
			pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT // 2 +self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
		if self.direction == 2:#vertical screen fade down
			pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
		if self.fade_counter >= SCREEN_WIDTH:
			fade_complete = True

		return fade_complete


#create screen fades
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)
win_fade = ScreenFade(2, WHITE, 4)

#create buttons
start_button = button.Button(SCREEN_WIDTH // 2 -100  , SCREEN_HEIGHT // 2 - 150, start_img, 1)
menu_button = button.Button(SCREEN_WIDTH // 2 -100 , SCREEN_HEIGHT // 2 -40, menu_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 -100	 , SCREEN_HEIGHT // 2 + 70, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 -100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)
back_img = pygame.image.load('PROJECT/IMG/back.png').convert_alpha()
pause_img = pygame.image.load('PROJECT/IMG/pause.png').convert_alpha()
resume_img = pygame.image.load('PROJECT/IMG/resumen.png').convert_alpha()
back_button = button.Button(10,  10 , back_img, 1)
pause_button = button.Button(SCREEN_WIDTH - 40, 10 , pause_img,1)
resume_button = button.Button(SCREEN_WIDTH // 2 -100 , SCREEN_HEIGHT // 2 -40, resume_img, 1)
exit_home_button = button.Button(SCREEN_WIDTH // 2 -100	 , SCREEN_HEIGHT // 2 + 70, exit_img, 1)
#create sprite groups
Monster_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()



#create empty tile list
world_data = []
for row in range(ROWS):
	r = [-1] * COLS
	world_data.append(r)
#load in level data and create world
with open(f'PROJECT/level{level}_data.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)
world = World()
index =1
player, health_bar = world.process_data(world_data,index)

princess1 = pygame.image.load(f'PROJECT/IMG/Player1/Walk/0.png').convert_alpha() 
princess1= pygame.transform.scale(princess1, (70, 70))

princess2 = pygame.image.load(f'PROJECT/IMG/Player2/Walk/0.png').convert_alpha() 
princess2= pygame.transform.scale(princess2, (70, 70))

arrowLeft = pygame.image.load('PROJECT/IMG/left.png').convert_alpha()
arrowLeft= pygame.transform.scale(arrowLeft, (50, 50))
yNv = 200
yLoai =330
xAR = SCREEN_WIDTH / 2 
arLeft_button_nv = button.Button(xAR, yNv, arrowLeft, 1)
arLeft_button_loai = button.Button(xAR, yLoai, arrowLeft, 1)



arrowRight = pygame.image.load('PROJECT/IMG/right.png').convert_alpha()
arrowRight= pygame.transform.scale(arrowRight, (50, 50))
arRight_button_nv = button.Button(xAR +120, yNv, arrowRight, 1)
arRight_button_loai = button.Button(xAR +120, yLoai, arrowRight, 1)

Game_control = 0
loaiphim1 = pygame.image.load('PROJECT/IMG/BP1.png').convert_alpha()
loaiphim1= pygame.transform.scale(loaiphim1, (80, 80))

loaiphim2 = pygame.image.load('PROJECT/IMG/BP2.png').convert_alpha()
loaiphim2= pygame.transform.scale(loaiphim2, (80, 80))


run = True
home = True
pause_game = False
while run:

	clock.tick(FPS)
	draw_bg()
 
	#draw tile pannel and tiles
	#pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))
	
	for i in button_list:
		i.draw(screen)
 
	Score = 0
	
	if home == True:
		#draw menu
		screen.fill(BG)
		#add buttons
		if start_button.draw(screen):
			start_game = True
			start_intro = True
			home = False
		if exit_button.draw(screen):
			run = False
   
		if menu_button.draw(screen):
			menu_game = True
	elif start_game == True: 
		#update background
		draw_bg()
		Score = sum(1 for monster in Monster_group if not monster.alive) *10
		img=font.render(f'SCORE: {Score}', True, RED)
		screen.blit(img,(10, 65))
		#draw world map
		world.draw()
  
		#show player health
		health_bar.draw(player.health)
		#show bullet
		draw_text('BULLET: ', font, RED, 10, 40)
		for x in range(player.ammo):
			screen.blit(bullet_img, (100 + (x * 10), 45))
	


		player.update()
		player.draw()

		for Monster in Monster_group:
			Monster.ai()
			Monster.update()
			Monster.draw()

		#update and draw groups
		bullet_group.update()
		item_box_group.update()
  
		decoration_group.update()
		water_group.update()
		exit_group.update()
		bullet_group.draw(screen)
  
		item_box_group.draw(screen)
		water_group.draw(screen)
  
		decoration_group.draw(screen)
		exit_group.draw(screen)
  

		if level ==3:
				win_image = pygame.image.load("PROJECT/IMG/win.jpg")
				win_image = pygame.transform.scale(win_image, (800, 640))
				screen.blit(win_image, (SCREEN_HEIGHT/2 - win_image.get_width()/2 +80, SCREEN_HEIGHT/2 - win_image.get_height()/2))
				# win_fade.fade()
				# text = 'WIN'
				# font_size = 100  # Kích thước mới bạn muốn
				# font = pygame.font.Font(None, font_size)
				# img = font.render(text, True, 'green')
				# screen.blit(img,(SCREEN_HEIGHT/2+50,SCREEN_HEIGHT/2))
		# win_fade.fade()
		# screen.fill(PINK)
		# win_image = pygame.image.load("PROJECT/IMG/win.jpg")
		# win_image = pygame.transform.scale(win_image, (800, 640))
		# screen.blit(win_image, (SCREEN_HEIGHT/2 - win_image.get_width()/2 +80, SCREEN_HEIGHT/2 - win_image.get_height()/2))
  
		#update player actions
		if player.alive:      
			#shoot bullets
			if shoot:
				player.shoot()
			if player.in_air:
				player.update_action(2)#2: jump
			elif moving_left or moving_right:
				player.update_action(1)#1: run
			else:
				player.update_action(0)#0: idle
			screen_scroll, level_complete = player.move(moving_left, moving_right)
			bg_scroll -= screen_scroll
			#check if player has completed the level
			if level_complete:
				start_intro = True
				level += 1
				bg_scroll = 0
				world_data = reset_level()
				if level <= MAX_LEVELS:
					#load in level data and create world
					with open(f'PROJECT/level{level}_data.csv', newline='') as csvfile:
						reader = csv.reader(csvfile, delimiter=',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								world_data[x][y] = int(tile)
					world = World() 
					player, health_bar = world.process_data(world_data, index)	
			
		else:
			screen_scroll = 0
			if death_fade.fade():
				if restart_button.draw(screen):
					death_fade.fade_counter = 0
					start_intro = True
					bg_scroll = 0
					world_data = reset_level()
					#load in level data and create world
					with open(f'PROJECT/level{level}_data.csv', newline='') as csvfile:
						reader = csv.reader(csvfile, delimiter=',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								world_data[x][y] = int(tile)
					world = World()
					player, health_bar = world.process_data(world_data, index)
		if pause_button.draw(screen):
			start_game = False
			pause_game = True
	elif pause_game == True and start_game ==False :
		screen.fill(BG)
		if exit_button.draw(screen):
			home = True
			pause_game = False
			if exit_button.clicked:
				index =1
				level = 1
				player, health_bar = world.process_data(world_data,index)
				
				Monster_group = pygame.sprite.Group()
				bullet_group = pygame.sprite.Group()
				item_box_group = pygame.sprite.Group()
				decoration_group = pygame.sprite.Group()
				water_group = pygame.sprite.Group()
				exit_group = pygame.sprite.Group()



				#create empty tile list
				world_data = []
				for row in range(ROWS):
					r = [-1] * COLS
					world_data.append(r)
				#load in level data and create world
				with open(f'PROJECT/level{level}_data.csv', newline='') as csvfile:
					reader = csv.reader(csvfile, delimiter=',')
					for x, row in enumerate(reader):
						for y, tile in enumerate(row):
							world_data[x][y] = int(tile)
				world = World()
				index =1
				player, health_bar = world.process_data(world_data,index)

				princess1 = pygame.image.load(f'PROJECT/IMG/Player1/Walk/0.png').convert_alpha() 
				princess1= pygame.transform.scale(princess1, (70, 70))

				princess2 = pygame.image.load(f'PROJECT/IMG/Player2/Walk/0.png').convert_alpha() 
				princess2= pygame.transform.scale(princess2, (70, 70))

				arrowLeft = pygame.image.load('PROJECT/IMG/left.png').convert_alpha()
				arrowLeft= pygame.transform.scale(arrowLeft, (50, 50))
				yNv = 200
				yLoai =330
				xAR = SCREEN_WIDTH / 2 
				arLeft_button_nv = button.Button(xAR, yNv, arrowLeft, 1)
				arLeft_button_loai = button.Button(xAR, yLoai, arrowLeft, 1)



				arrowRight = pygame.image.load('PROJECT/IMG/right.png').convert_alpha()
				arrowRight= pygame.transform.scale(arrowRight, (50, 50))
				arRight_button_nv = button.Button(xAR +120, yNv, arrowRight, 1)
				arRight_button_loai = button.Button(xAR +120, yLoai, arrowRight, 1)

				Game_control = 0
				loaiphim1 = pygame.image.load('PROJECT/IMG/BP1.png').convert_alpha()
				loaiphim1= pygame.transform.scale(loaiphim1, (80, 80))

				loaiphim2 = pygame.image.load('PROJECT/IMG/BP2.png').convert_alpha()
				loaiphim2= pygame.transform.scale(loaiphim2, (80, 80))



		if resume_button.draw(screen):
			start_game = True
			menu_game = False
			pause_game = False

	if menu_game == True:
		screen.fill(BG)

		# font = pygame.font.SysFont('Arial', 32, bold=True)

		choose_nv = font.render("Choose", True, (205, 85, 85))
		screen.blit(choose_nv, (SCREEN_WIDTH / 2 - 120, SCREEN_HEIGHT / 2 - 120))
		
		flag_check_index = True

		if index==1 and arLeft_button_nv.draw(screen):
			index=2
			flag_check_index = False

		if index==1 and arRight_button_nv.draw(screen):
			index=2
			flag_check_index = False

		if index==2 and arLeft_button_nv.draw(screen):
			index=1
			flag_check_index = False

		if index==2 and arRight_button_nv.draw(screen):
			index=1
			flag_check_index = False

		if index==1:
			screen.blit(princess1, (xAR+50, yNv))
		elif index ==2:
			screen.blit(princess2, (xAR+50, yNv))
			
			Monster_group = pygame.sprite.Group()
			bullet_group = pygame.sprite.Group()
			item_box_group = pygame.sprite.Group()
			decoration_group = pygame.sprite.Group()
			water_group = pygame.sprite.Group()
			exit_group = pygame.sprite.Group()
			#create empty tile list
			world_data = []
			for row in range(ROWS):
				r = [-1] * COLS
				world_data.append(r)
			#load in level data and create world
			with open(f'PROJECT/level{level}_data.csv', newline='') as csvfile:
				reader = csv.reader(csvfile, delimiter=',')
				for x, row in enumerate(reader):
					for y, tile in enumerate(row):
						world_data[x][y] = int(tile)
			world = World()
			player, health_bar = world.process_data(world_data,index)
		if flag_check_index == False:
			player, health_bar = world.process_data(world_data,index)

			
		choose_loai = font.render("Choose", True, (205, 85, 85))
		screen.blit(choose_loai, (SCREEN_WIDTH / 2 - 120, SCREEN_HEIGHT / 2 + 10))

		if Game_control == 0 and arLeft_button_loai.draw(screen):
			Game_control = 1
		if Game_control ==0 and arRight_button_loai.draw(screen):
			Game_control = 1
		if Game_control == 1 and arLeft_button_loai.draw(screen):
			Game_control = 0
		if Game_control ==1 and arRight_button_loai.draw(screen):
			Game_control = 0
		if Game_control == 0:
			screen.blit(loaiphim1, (xAR+50, yLoai))
		else:
			screen.blit(loaiphim2, (xAR+50, yLoai))
		if back_button.draw(screen):
			menu_game = False

	for event in pygame.event.get():
		#quit game
		if event.type == pygame.QUIT:
			run = False
		#keyboard presses
		
		if event.type == pygame.KEYDOWN:
			if Game_control == 0:
				if event.key == pygame.K_a:
					moving_left = True
				if event.key == pygame.K_d:
					moving_right = True
				if event.key == pygame.K_SPACE:
					shoot = True
				if event.key == pygame.K_w and player.alive:
					player.jump = True
					jump_fx.play()
				if event.key == pygame.K_ESCAPE:
					run = False
			if Game_control == 1:
				if event.key == pygame.K_LEFT:
					moving_left = True
				if event.key == pygame.K_RIGHT:
					moving_right = True
				if event.key == pygame.K_SPACE:
					shoot = True
				if event.key == pygame.K_q:
					grenade = True
				if event.key == pygame.K_UP and player.alive:
					player.jump = True
					jump_fx.play()
				if event.key == pygame.K_ESCAPE:
					run = False



		#keyboard button released
		if event.type == pygame.KEYUP:
			if Game_control == 0:
				if event.key == pygame.K_a:
					moving_left = False
				if event.key == pygame.K_d:
					moving_right = False
				if event.key == pygame.K_SPACE:
					shoot = False
			if Game_control == 1:
				if event.key == pygame.K_LEFT:
					moving_left = False
				if event.key == pygame.K_RIGHT:
					moving_right = False
				if event.key == pygame.K_SPACE:
					shoot = False
		






		
  
	pygame.display.update()

pygame.quit()
print(Princess.__doc__)