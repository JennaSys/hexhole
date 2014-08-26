import math

hex_size = 1.0
drill_size = 0.25
corners = 6

side_angle = 360 / corners
center_to_flat = (hex_size / 2)
center_to_corner = center_to_flat / math.cos(math.radians(30))
flat_length = 2 * (center_to_flat * math.tan(math.radians(side_angle/2)))  # == center_to_corner

drill_radius = drill_size / 2
center_to_drill = center_to_corner - drill_radius

small_chord = drill_size/2
# overdrill_area = (((drill_radius**2) * math.pi) / corners) - ((drill_radius**2) * ((3**0.5)/4))  # area of circle sector - equilateral triangle
#overdrill_area = ((drill_radius**2) / 2) * (((math.pi / 180) * side_angle) - math.sin(math.radians(side_angle)))  # area of circle segment degrees
overdrill_area = ((drill_radius**2) / 2) * (math.radians(side_angle) - math.sin(math.radians(side_angle))) * 2  # area of circle segment radians


# calc intersecting angle using law of cos:  A=acos((R^2 + d^2 - r^2)/ 2Rd)
# given angle, calc intersecting chord:  c=2(R*sin(A))
# given angle, calc large segment:  area=(2A - sin(2A)) * R^2) / 2
# given chord, calc small angle: a = asin((c/2) / r)
# given small angle, calc small segment:  (2a - sin(2a)) * r^2) / 2
intersecting_angle_large = math.acos((center_to_flat**2 + center_to_drill**2 - drill_radius**2) / (2 * center_to_flat * center_to_drill))
intersecting_chord = 2 * center_to_flat * math.sin(intersecting_angle_large)
large_segment_area = (((2 * intersecting_angle_large) - math.sin(2 * intersecting_angle_large)) * (center_to_flat**2)) / 2
intersecting_angle_small = math.asin((intersecting_chord/2) / drill_radius)
small_segment_area = (((2 * intersecting_angle_small) - math.sin(2 * intersecting_angle_small)) * (drill_radius**2)) / 2

print "intersecting_angle_large=", math.degrees(intersecting_angle_large)
print "intersecting_chord=", intersecting_chord
print "large_segment_area=", large_segment_area
print "intersecting_angle_small=", math.degrees(intersecting_angle_small)
print "small_segment_area=", small_segment_area
print

# calc included hex triangle: ab/2 * 2
# subtract 60deg large segment: (pi r^2)/6
# subtract area defined by:
#     small segment - large segment - overdrill_area

hex_area = ((flat_length / 2 ) * center_to_flat )
drill_area = ((center_to_flat**2) * math.pi) / corners
corner_area = small_segment_area - large_segment_area - overdrill_area
underdrill_area = hex_area - drill_area - corner_area

print "hex_area=", hex_area
print "drill_area=", drill_area
print "corner_area=", corner_area
print "underdrill_area=", underdrill_area
print


print "Hex Size: {:.4f}".format(hex_size)
print "Center to Flat: {:.4f}".format(center_to_flat)
print "Center to Corner: {:.4f}".format(center_to_corner)
print "Corner to Corner: {:.4f}".format(center_to_corner * 2)
print "Flat Length: {:.4f}".format(flat_length)
print
print "Center Drill Size: {:.3f}".format(hex_size)
print "Corner Drill Size: {:.3f}".format(drill_size)
print

for corner in range(corners):
    x_offset = center_to_drill * math.cos(math.radians(corner * side_angle))
    y_offset = center_to_drill * math.sin(math.radians(corner * side_angle))
    print "Corner {0}: X={1:.4f}  Y={2:.4f}".format(corner + 1, x_offset, y_offset)

print
print "Over drill area: ", overdrill_area
print "Under drill area: ", underdrill_area

