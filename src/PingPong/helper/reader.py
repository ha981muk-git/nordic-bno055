class ReadLine:
    def __init__(self, serial_device):
        self.buf = bytearray()
        self.serial_device = serial_device

    def readline(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            r = self.buf[: i + 1]
            self.buf = self.buf[i + 1 :]
            return r
        while True:
            i = max(1, min(2048, self.serial_device.in_waiting))
            data = self.serial_device.read(i)
            i = data.find(b"\n")
            if i >= 0:
                r = self.buf + data[: i + 1]
                self.buf[0:] = data[i + 1 :]
                return r
            else:
                self.buf.extend(data)

