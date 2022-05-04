import threading
from time import sleep


class Camera(object):
    def __init__(self, process):
        self.to_process = []
        self.to_output = []
        self.process = process
        thread = threading.Thread(target=self.keep_processing, args=())
        thread.daemon = True
        thread.start()

    def process_one(self):
        if not self.to_process:
            return

        # input is an ascii string.
        #input_str = self.to_process.pop(0)

        # convert it to a pil image
        #input_img = base64_to_pil_image(input_str)

        ################## where the hard work is done ############
        # output_img is an PIL image
        # output_img = self.makeup_artist.apply_makeup(input_img)
        #output_img = self.process.process(input_img)

        # open_cv_image = np.array(input_img)
        # # Convert RGB to BGR
        # open_cv_image = open_cv_image[:, :, ::-1].copy()
        # gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)


        # img = cv2.cvtColor(gray, cv2.COLOR_BGR2RGB)
        # im_pil = Image.fromarray(img)

        # output_img = im_pil




        # output_str is a base64 string in ascii
        #output_str = pil_image_to_base64(output_img)

        # convert eh base64 string in ascii to base64 string in _bytes_
        #self.to_output.append(binascii.a2b_base64(output_str))

    def keep_processing(self):
        while True:
            self.process_one()
            sleep(0.01)

    def enqueue_input(self, input):
        self.to_process.append(input)

    def get_frame(self):
        while not self.to_output:
            sleep(0.05)
        return self.to_output.pop(0)
