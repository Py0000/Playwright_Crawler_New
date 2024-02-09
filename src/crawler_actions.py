import time
import random

async def move_mouse_smoothly_top_left_bottom_right(page):
    steps = random.randint(3,5)

    start_x = 0
    start_y = 0

    # Get the size of the page
    page_size = await page.evaluate('''() => ({ width: document.documentElement.clientWidth, height: document.documentElement.clientHeight })''')
    end_x, end_y = page_size['width'], page_size['height']

    step_size_x = (end_x - start_x) / steps
    step_size_y = (end_y - start_y) / steps

    for i in range(steps + 1):
        x = start_x + step_size_x * i
        y = start_y + step_size_y * i

        # Move the mouse to the calculated coordinates
        await page.mouse.move(x, y)

        # Add a small delay to simulate smooth movement (adjust the time for your desired smoothness)
        time.sleep(random.uniform(0.001, 0.003))


async def move_mouse_smoothly_bottom_right_top_left(page):
    steps = random.randint(3,5)

    # Get the size of the page
    page_size = await page.evaluate('''() => ({ width: document.documentElement.clientWidth, height: document.documentElement.clientHeight })''')
    start_x, start_y = page_size['width'], page_size['height']

    end_x = 0
    end_y = 0

    step_size_x = (end_x - start_x) / steps
    step_size_y = (end_y - start_y) / steps

    for i in range(steps + 1):
        x = start_x + step_size_x * i
        y = start_y + step_size_y * i

        # Move the mouse to the calculated coordinates
        await page.mouse.move(x, y)

        # Add a small delay to simulate smooth movement (adjust the time for your desired smoothness)
        time.sleep(random.uniform(0.001, 0.003))


async def move_mouse_smoothly(page):
    repeat_num = random.randint(2, 3)
    try:
        for i in range(repeat_num):
            await move_mouse_smoothly_top_left_bottom_right(page)
            await move_mouse_smoothly_bottom_right_top_left(page)
            time.sleep(random.uniform(0.001, 0.003))

        print("Mouse Move Successfully")
        status = "Success"
    
    except Exception as e:
        print("Error moving mouse: ", e)
        status = "Failed"
    
    finally:
        return status

async def dismiss_js_alert(page):
    try:
        await page.on("dialog", lambda dialog: dialog.accept())
    except Exception as e:
        pass

async def execute_user_action(page):
    await dismiss_js_alert(page)
    move_status = await move_mouse_smoothly(page)
    return move_status