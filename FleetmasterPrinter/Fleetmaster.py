import pyautogui as py
import pyscreeze as ps
import time
import pygame

# Install opencv_python

# Set up the screen
pygame.init()
pygame.display.set_caption("Fleetmaster PDF Printer")
pygame.display.set_icon(pygame.image.load("FleetmasterPrinter/img/monitor.png"))

def main():
    
    # Set up the window
    screen = pygame.display.set_mode((800, 600))
    
    RUNNING = True
    
    # Title
    font = pygame.font.Font(None, 70)
    text = font.render("Fleetmaster PDF Printer", True, (255, 255, 255))
    text_rect = text.get_rect(center=(400, 50))
    
    # Input Box
    input_box = pygame.Rect(25, 200, 750, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    current_text = ""
    font = pygame.font.Font(None, 32)
    text_surface = font.render("", True, color)
    
    # Label
    label2 = font.render("Enter reg numbers, use ' , ' between each", True, (255, 255, 255))
    label2_rect = label2.get_rect(center=(400, 275))
    
    # Button
    button = pygame.Rect(300, 325, 200, 50)
    button_color = (0, 128, 255)
    button_text = font.render("Print", True, (255, 255, 255))
    button_text_rect = button_text.get_rect(center=(400, 350))

    # Label
    label = font.render("You must have 'Fleetmaster' bookmarked and have the browser visible.", True, (255, 255, 255))
    label_rect = label.get_rect(center=(400, 500))
    
    while RUNNING:
        
        screen.fill((71, 71, 71))
        screen.blit(text, text_rect)
    
        # Input Box
        pygame.draw.rect(screen, color, input_box, 2)
        screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))
        input_box.w = max(750, text_surface.get_width() + 10)
        
        # Label
        screen.blit(label2, label2_rect)
        
        # Button
        pygame.draw.rect(screen, button_color, button)
        screen.blit(button_text, button_text_rect)
        
        # Label
        screen.blit(label, label_rect)
        
        for event in pygame.event.get():
            
            if event.type == pygame.MOUSEMOTION:
                if button.collidepoint(event.pos):
                    button_color = (200, 128, 255)
                else:
                    button_color = (0, 128, 255)
                
            if event.type == pygame.QUIT:
                RUNNING = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
                
                if button.collidepoint(event.pos):
                    if current_text == "" or len(current_text) < 7:
                        continue
                    arr = current_text.split(",")
                    func(arr)
                    current_text = ""
                    text_surface = font.render(current_text, True, color)
                
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        arr = current_text.split(",")
                        func(arr)
                        current_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        current_text = current_text[:-1]
                    else:
                        if (len(current_text) <= 62):
                            current_text += event.unicode
                    text_surface = font.render(current_text, True, color)
                
        pygame.display.flip()
    pygame.quit()

def func(arr_of_regs):
    
    for reg in arr_of_regs:

        time.sleep(1)
        found = False
        while not found:
            try:
                box = ps.locateOnScreen("FleetmasterPrinter/img/Fleetmaster_white.png", confidence=0.7)
                center = py.center(box)
                py.moveTo(center.x, center.y)
                py.click()
                found = True
            except:
                continue
            
        time.sleep(2)
        # # Click Vehicle Tab
        # found = False
        # while not found:
        #     try:
        #         box = py.locateOnScreen("FleetmasterPrinter/img/Vehicles.png", confidence=0.6)
        #         center = py.center(box)
        #         py.moveTo(center.x, center.y) 
        #         py.click()
        #         found = True
        #     except:
        #         continue
            
        # Click "Enter a keyword"
        found = False
        while not found:
            try:
                box = py.locateOnScreen("FleetmasterPrinter/img/Search.png", confidence=0.8)
                center = py.center(box)
                py.moveTo(center.x, center.y)
                py.click()
                found = True
            except:
                continue
        
        # Type the registration number
        py.typewrite(reg)

        time.sleep(2)

        # Click result
        found = False
        while not found:
            try:
                box = py.locateOnScreen("FleetmasterPrinter/img/1item.png", confidence=0.8)
                center = py.center(box)
                py.moveTo(center.x - 50, center.y - 50)
                py.click()
                found = True
            except:
                continue

        # Click "Actions"
        found = False
        while not found:
            try:
                box = py.locateOnScreen("FleetmasterPrinter/img/Actions.png", confidence=0.8)
                center = py.center(box)
                py.moveTo(center.x, center.y)
                py.click()
                found = True
            except:
                continue
        
        # Click "Download"
        found = False
        while not found:
            try:
                box = py.locateOnScreen("FleetmasterPrinter/img/Download.png", confidence=0.8)
                center = py.center(box)
                py.moveTo(center.x, center.y)
                py.click()
                found = True
            except:
                continue
            
        time.sleep(2)
        
        # Click PDF Icon
        found = False
        while not found:
            try:
                box = py.locateOnScreen("FleetmasterPrinter/img/pdf.png", confidence=0.8)
                center = py.center(box)
                py.moveTo(center.x, center.y)
                py.click()
                found = True
            except:
                continue
            
        time.sleep(1)
        py.hotkey('ctrl', 'p')
        time.sleep(2)
        py.press('enter')
        # time.sleep(2)
        # py.hotkey('ctrl', 'p')
        # time.sleep(2)
        # py.press('enter')
        time.sleep(2)

main()