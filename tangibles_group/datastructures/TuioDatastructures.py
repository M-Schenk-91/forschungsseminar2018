
from parsers.MessageTypes import MessageTypes


class TUIOPointer:
    """
    /tuio2/ptr s_id tu_id c_id x_pos y_pos angle shear radius press [x_vel y_vel p_vel m_acc p_acc]
    /tuio2/ptr int32 int32 int32 float float float float float [float float float float float]
    """

    def __init__(self, session_id, type_user_id, class_id, x, y, angle, shear, radius, press, xvel, yvel, pvel, macc, pacc):
        ids = ('0' * (32 - len(bin(type_user_id)[2:]))) + bin(type_user_id)[2:]

        self.session_id = session_id
        self.type_id = int('0b' + ids[16:], 2)
        self.user_id = int('0b' + ids[:16], 2)
        self.class_id = class_id
        self.x = x
        self.y = y
        self.angle = angle
        self.shear = shear
        self.radius = radius
        self.press = press
        self.xvel = xvel
        self.yvel = yvel
        self.pvel = pvel
        self.macc = macc
        self.pacc = pacc

    def __repr__(self):
        return '{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, {13}, {14}'.format(self.session_id,
                                                                                                 self.type_id, self.user_id,
                                                                                                 self.class_id, self.x,
                                                                                                 self.y, self.angle,
                                                                                                 self.shear,
                                                                                                 self.radius,
                                                                                                 self.press, self.xvel,
                                                                                                 self.yvel, self.pvel,
                                                                                                 self.macc, self.pacc)


class TUIOBounds:
    """
    /tuio2/bnd s_id x_pos y_pos angle width height area [x_vel y_vel a_vel m_acc r_acc]
    /tuio2/bnd int32 float float float float float float [float float float float float]
    """

    def __init__(self, session_id, x, y, angle, width, height, area, xvel, yvel, avel, macc, racc):
        self.session_id = session_id
        self.x = x
        self.y = y
        self.angle = angle
        self.width = width
        self.height = height
        self.area = area
        self.xvel = xvel
        self.yvel = yvel
        self.avel = avel
        self.macc = macc
        self.racc = racc

    def __repr__(self):
        return '{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}'.format(self.session_id, self.x, self.y,
                                                                                    self.angle, self.width, self.height,
                                                                                    self.area, self.xvel, self.yvel,
                                                                                    self.avel, self.macc, self.racc)

    def get_position(self):
        return self.x, self.y


class TUIOSymbol:
    """
    /tuio2/sym s_id tu_id c_id group data
    /tuio2/sym int32 int32 int32 string string
    """

    def __init__(self, session_id, type_user_id, class_id, group, data):
        ids = ('0' * (32 - len(bin(type_user_id)[2:]))) + bin(type_user_id)[2:]

        self.session_id = session_id
        self.type_id = int('0b' + ids[16:], 2)
        self.user_id = int('0b' + ids[:16], 2)
        self.class_id = class_id
        self.group = group
        self.data = data

    def __repr__(self):
        return '{0}, {1}, {2}, {3}, {4}, {5}'


class TUIOToken:
    """
    /tuio2/tok s_id tu_id c_id x_pos y_pos angle [x_vel y_vel a_vel m_acc r_acc]
    /tuio2/tok int32 int32 int32 float float float [float float float float float]
    """

    def __init__(self, session_id, type_user_id, class_id, x, y, angle, xvel, yvel, avel, macc, racc):
        ids = ('0' * (32 - len(bin(type_user_id)[2:]))) + bin(type_user_id)[2:]

        self.session_id = session_id
        self.type_id = int('0b' + ids[16:], 2)
        self.user_id = int('0b' + ids[:16], 2)
        self.class_id = class_id
        self.x = x
        self.y = y
        self.angle = angle
        self.xvel = xvel
        self.yvel = yvel
        self.avel = avel
        self.macc = macc
        self.racc = racc

    def __repr__(self):
        return '{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}'.format(self.session_id, self.type_id, self.user_id,
                                                                               self.class_id, self.x, self.y,
                                                                               self.angle, self.xvel, self.yvel,
                                                                               self.avel, self.macc, self.racc)


class TUIOObject:

    def __init__(self, session_id, ptr, bnd, sym, tok, frm):
        self.components = {
            'ptr': ptr,
            'bnd': bnd,
            'sym': sym,
            'tok': tok,
            'frm': frm
        }

        self.session_id = session_id

    def __repr__(self):
        return '\ns_id: {0}\nptr: {1}\nbnd: {2}\nsym: {3}\ntok: {4}\nframe:\n\tnum: {5}\n\ttime: {6}\n\ttime_fraction: {7} \n\tdim: {8}\n\tsrc: {9}\n'.format(self.session_id,
                                                                                      self.components['ptr'],
                                                                                      self.components['bnd'],
                                                                                      self.components['sym'],
                                                                                      self.components['tok'],
                                                                                      self.components['frm']['num'],
                                                                                      self.components['frm']['t'],
                                                                                      self.components['frm']['s_fraction'],
                                                                                      self.components['frm']['dim'],
                                                                                      self.components['frm']['src'])

    def set_pointer_component(self, value):
        self.components['ptr'] = value

    def set_bounds_component(self, value):
        self.components['bnd'] = value

    def set_source_component(self, value):
        self.components['src'] = value

    def set_symbol_component(self, value):
        self.components['sym'] = value

    def set_token_component(self, value):
        self.components['tok'] = value

    def set_frame_component(self, value):
        self.components['frm'] = value

    def set_frame_number_component(self, value):
        self.components['frm']['num'] = value

    def set_frame_time_component(self, value):
        self.components['frm']['t'] = value

    def set_frame_time_fraction_component(self, value):
        self.components['frm']['s_fraction'] = value

    def set_frame_dimension_component(self, value):
        self.components['frm']['dim'] = value

    def set_frame_source_component(self, value):
        self.components['frm']['src'] = value

    def get_all_components(self):
        return self.components

    def get_pointer_component(self):
        return self.components['ptr']

    def get_bounds_component(self):
        return self.components['bnd']

    def get_source_component(self):
        return self.components['src']

    def get_symbol_component(self):
        return self.components['sym']

    def get_token_component(self):
        return self.components['tok']

    def get_frame_component(self):
        return self.components['frm']

    def get_frame_number_component(self):
        return self.components['frm']['num']

    def get_frame_time_component(self):
        return self.components['frm']['t']

    def get_frame_time_fraction_component(self):
        return self.components['frm']['s_fraction']

    def get_frame_dimension_component(self):
        return self.components['frm']['dim']

    def get_frame_source_component(self):
        return self.components['frm']['src']

    def get_session_id(self):
        return self.session_id

    def get_type_id(self):
        return self.get_token_component().type_id

    def get_user_id(self):
        return self.get_token_component().user_id

    def get_class_id(self):
        return self.get_token_component().class_id

    @staticmethod
    def create_tuio_pointer(data):
        return TUIOPointer(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9],
                           data[10], data[11], data[12], data[13])

    @staticmethod
    def create_tuio_bounds(data):
        return TUIOBounds(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9],
                          data[10], data[11])

    @staticmethod
    def create_tuio_token(data):
        return TUIOToken(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9],
                         data[10])

    @staticmethod
    def create_tuio_symbol(data):
        return TUIOSymbol(data[0], data[1], data[2], data[3], data[4])

    @staticmethod
    def create_tuio_object(session_id, bundle, frame):
        ptr = bnd = sym = tok = None

        for element in bundle:
            if element[0] == MessageTypes.POINTER.value:
                ptr = TUIOObject.create_tuio_pointer(element[1:])
            elif element[0] == MessageTypes.BOUNDS.value:
                bnd = TUIOObject.create_tuio_bounds(element[1:])
            elif element[0] == MessageTypes.TOKEN.value:
                tok = TUIOObject.create_tuio_token(element[1:])
            elif element[0] == MessageTypes.SYMBOL.value:
                sym = TUIOObject.create_tuio_symbol(element[1:])

        return TUIOObject(session_id, ptr, bnd, sym, tok, frame)
