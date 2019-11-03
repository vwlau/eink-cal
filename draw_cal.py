from PIL import Image,ImageDraw,ImageFont
import calendar
import datetime
import dateutil.parser


#draw rounded rectangles given the side coordinates, cornder diameter, fill, and width
def rounded_rect(draw, left, top, right, bottom, dia, f, wid):

    #draw the rounded corners
    draw.arc([(left, top),(left + dia,top + dia)], 180, 270, fill=f, width=wid) #top left
    draw.arc([(right - dia, top),(right, top + dia)], 270, 0, fill=f, width=wid) #top right
    draw.arc([(left, bottom - dia),(left + dia, bottom)], 90, 180, fill=f, width=wid) #bottom left
    draw.arc([(right - dia, bottom-dia),(right, bottom)], 0, 90, fill=f, width=wid) #bottom right

    #connect the corners
    draw.line([(left + dia/2, top),(right - dia/2, top)], fill=f, width=wid) #top
    draw.line([(left + dia/2, bottom),(right - dia/2, bottom)], fill=f, width=wid) #bottom
    draw.line([(left, top + dia/2),(left, bottom - dia/2)], fill=f, width=wid) #left
    draw.line([(right, top + dia/2),(right, bottom - dia/2)], fill=f, width=wid) #right

#draw filled rounded rectangles given the side coordinates, cornder diameter, and fill
def filled_rounded_rect(draw, left, top, right, bottom, dia, f):

    #fill the corners
    draw.pieslice([(left, top),(left + dia,top + dia)], 180, 270, fill=f) #top left
    draw.pieslice([(right - dia, top),(right, top + dia)], 270, 0, fill=f) #top right
    draw.pieslice([(left, bottom - dia),(left + dia, bottom)], 90, 180, fill=f) #bottom left
    draw.pieslice([(right - dia, bottom-dia),(right, bottom)], 0, 90, fill=f) #bottom right

    #fill rectangles
    draw.rectangle([(left + dia/2, top),(right - dia/2, bottom)], fill=f) #tall rect
    draw.rectangle([(left, top + dia/2),(right, bottom - dia/2)], fill=f) #wide rect

#too lazy to figure out a generalized dotted line
#x1 >= x0
def horiz_dotted_line(draw, x0, y0, x1, sp, f):

    w_span = int(x1 - x0)

    for x in range(0, w_span, sp):
        draw.point([x0 + x,y0], fill=f)

#fill area bounded by top left and bottom right corners with pixel spacing, sp
#x1 >= x0 & y1 >= y0
def dotted_fill(draw, x0, y0, x1, y1, sp, f):

    w_span = x1 - x0
    h_span = y1 - y0

    for i in range(0, w_span, sp):
        for j in range(0, h_span, sp):
            draw.point([x0 + i,y0 + j], fill=f)

#centers text horizontally and vertically within a box
#x_adjust is just in case
#y_adjust is necessary for different height letters messing with the centering
def centered_text(draw, text, font, left, top, right, bottom, x_adjust, y_adjust):

    text_size = draw.textsize(text, font)
    text_w = text_size[0]
    text_h = text_size[1]

    box_w = right - left
    box_h = bottom - top

    text_left = left + int((box_w - text_w)/2)
    text_top = top + int((box_h - text_h)/2)

    draw.text((text_left + x_adjust, text_top + y_adjust), text, font=font)

'''
draw calendar grid 
'''
def draw_cal(draw, screen_w, screen_h, day_view_divider, cal_divider, today):

    cal_padding = 6
    header_h = 22

    day_w = int((day_view_divider-cal_padding*2)/7)
    day_h = int((screen_h - cal_divider - header_h - cal_padding*2)/5)
    
    cal_bottom = screen_h - cal_padding
    cal_top = cal_bottom - day_h * 5
    cal_left = cal_padding
    cal_right = cal_left + day_w * 7
    header_top = cal_top - header_h

    #draw internal week lines
    for x in range(1,6):
        week_line = cal_bottom - day_h * x
        draw.line([(cal_left,week_line),(cal_right,week_line)], fill=0, width=1)

    #draw internal day lines
    for x in range(1,7):
        day_line = cal_left + day_w * x
        draw.line([(day_line, header_top),(day_line,cal_bottom)], fill=0, width=1)

    #draw external cal lines
    arc_d = 24
    rounded_rect(draw, cal_left, header_top, cal_right, cal_bottom, arc_d, 0, 1)

    #calendar calculations
    this_month = calendar.Calendar(firstweekday=6)
    #returns calendar as list of date objects
    this_month_cal = this_month.monthdatescalendar(today.year,today.month)

    #calendar.setfirstweekday(calendar.SUNDAY)
    #cal_weekheader = calendar.weekheader(3)
    cal_weekheader = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']

    font16 = ImageFont.truetype('./fonts/mononoki-Regular.ttf', 16)

    #draw day of week header/column titles
    header_w_offset = 8
    header_h_offset = 6
    for x in range(len(cal_weekheader)):
        font_offset = font16.getoffset(cal_weekheader[x])
        draw.text((cal_left + header_w_offset - font_offset[0] + day_w * x, header_top + header_h_offset - font_offset[1]), cal_weekheader[x], font=font16)

    #draw all numbers on calendar
    num_w_offset = 8 #width offset from corner of day box
    num_h_offset = 8 #height offset from corner of day box
    marker_offset = 4 #offset from corner of day box
    marker_w = 26 #marker width
    marker_h = 18 #marker height
    m_arc_d = 12 #marker corner arc diameter

    for i in range(len(this_month_cal)):
        for j in range(len(this_month_cal[i])):
            font_offset = font16.getoffset(str(this_month_cal[i][j].day))
            #dotted filled the days that are not part of this month
            if this_month_cal[i][j].month is not today.month:
                dotted_fill(draw, cal_left + day_w * j, cal_top + day_h * i, cal_left + day_w * (j + 1), cal_top + day_h * (i + 1), 2, 0)
                #hack to get rid of stray pixels in the bottom right corner
                if (i == len(this_month_cal)-1) and (j == len(this_month_cal[i])-1):
                    draw.polygon([(cal_left + day_w * (j + 1), cal_top + day_h * (i + 1)), 
                                  (cal_left + day_w * (j + 1) - arc_d/4, cal_top + day_h * (i + 1)), 
                                  (cal_left + day_w * (j + 1), cal_top + day_h * (i + 1) - arc_d/4)], 
                                   fill=255)
            #put marker on today's date
            if this_month_cal[i][j].day == today.day:
                marker_left = cal_left + marker_offset + day_w * j
                marker_top = cal_top + marker_offset + day_h * i
                marker_right = marker_left + marker_w
                marker_bottom = marker_top + marker_h
                filled_rounded_rect(draw, marker_left, marker_top, marker_right, marker_bottom, m_arc_d, 0)
                draw.text((cal_left + num_w_offset - font_offset[0] + day_w * j, cal_top + num_h_offset - font_offset[1] + day_h * i), str(this_month_cal[i][j].day), fill=255, font=font16)
            else:
                draw.text((cal_left + num_w_offset - font_offset[0] + day_w * j, cal_top + num_h_offset - font_offset[1] + day_h * i), str(this_month_cal[i][j].day), font=font16)

def draw_two_day_view(draw, screen_w, screen_h, day_view_divider, hour_start, hours_shown, today, work_events):

    hour_label_w = 30

    block_w = int(((screen_w - day_view_divider) - hour_label_w)/2)
    sep_coord = screen_w - block_w
    block_h = int(screen_h/(hours_shown+1))
    header_h = screen_h - block_h * hours_shown

    #draw header line
    draw.line([(day_view_divider, header_h), (screen_w, header_h)], fill=0, width=2)
    #write in the headers
    font22 = ImageFont.truetype('./fonts/mononoki-Regular.ttf', 22)
    centered_text(draw, 'Today', font22, day_view_divider + hour_label_w, 0, sep_coord, header_h, 0, 0)
    centered_text(draw, 'Tomorrow', font22, sep_coord, 0, screen_w, header_h, 0, -3)
    #draw hour label seperator
    draw.line([(day_view_divider + hour_label_w, 0), (day_view_divider + hour_label_w, screen_h)], fill=0, width=2)
    #draw day seperator
    draw.line([(sep_coord, 0), (sep_coord, screen_h)], fill=0, width=2)

    #create list of the hour labels
    hours_list = []
    for x in range(hour_start, hour_start + hours_shown):
        twelve_hr_time = x % 12
        if twelve_hr_time == 0:
            twelve_hr_time = 12
        if len(str(twelve_hr_time)) == 1:
            hours_list.append('0'+str(twelve_hr_time))
        else:
            hours_list.append(str(twelve_hr_time))

    #write the hour labels and draw the hour separation lines
    #solid lines commented out
    font16 = ImageFont.truetype('./fonts/mononoki-Regular.ttf', 16)
    for i in range(len(hours_list)):
        centered_text(draw, hours_list[i], font16, day_view_divider, header_h + block_h * i, day_view_divider + hour_label_w, header_h + block_h * (i+1), 0, 0)
        #draw.line([(day_view_divider, header_h + block_h * (i + 1)),(screen_w, header_h + block_h * (i + 1))])
        horiz_dotted_line(draw, day_view_divider, header_h + block_h * (i + 1), screen_w, 2, 0)

    font32 = ImageFont.truetype('./fonts/mononoki-Regular.ttf', 32)
    if len(work_events) > 0:
        for event in work_events:
            event_title = event[0]
            event_start_dt = dateutil.parser.parse(event[1])
            event_end_dt = dateutil.parser.parse(event[2])
            event_length = (event_end_dt - event_start_dt).seconds/3600
            delta_from_start = event_start_dt.hour - hour_start
            day_offset = event_start_dt.day - today.day
            #+4 on the left coord and -3 on the right coord because of line widths
            #white out the event area
            filled_rounded_rect(draw, day_view_divider + hour_label_w + block_w * day_offset + 4, 
                                header_h + block_h * delta_from_start, 
                                sep_coord + block_w * day_offset - 3, 
                                header_h + block_h * (delta_from_start + event_length), 
                                20, 255)
            #draw rounded rect for event area
            rounded_rect(draw, day_view_divider + hour_label_w + block_w * day_offset + 4, 
                         header_h + block_h * delta_from_start, 
                         sep_coord + block_w * day_offset - 3, 
                         header_h + block_h * (delta_from_start + event_length), 
                         20, 0, 2)
            #put centered text in event area
            centered_text(draw, event_title, font32, day_view_divider + hour_label_w + block_w * day_offset + 4,
                          header_h + block_h * delta_from_start, 
                          sep_coord + block_w * day_offset - 3, 
                          header_h + block_h * (delta_from_start + event_length), 0, 0)


if __name__ == '__main__':

    screen_w = 640
    screen_h = 384
    day_view_divider = screen_w/2
    cal_divider = screen_h/2

    image = Image.new('1', (screen_w,screen_h), color=1)

    draw = ImageDraw.Draw(image)

    #center divider line
    draw.line([(day_view_divider,0),(day_view_divider,screen_h)], fill=0, width=2)

    today = datetime.date.today()
    draw_cal(draw, screen_w, screen_h, day_view_divider, cal_divider, today)

    draw_two_day_view(draw, screen_w, screen_h, day_view_divider, 7, 17, today, [])

    image.show()
