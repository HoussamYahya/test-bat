import sys

sys.path.append('C:\\Projet\\Python_bench_Git_Test\\pythontestbench\\Libs')
import NI_8012 as NI_8012
from pytest import mark
import time
import subprocess
from subprocess import PIPE, STDOUT

NI_VIRTUAL_BENCH_NAME = "VB8012-31A1DBE"
stantby_current_conso = 0.007  # ]0.006 : 0.007] sum of current POS and NEG (virtualbench)
oprational_current_conso = 0.045  # sum of current POS and NEG (virtualbench)


@mark.statemachine_smoke
class TestDownload:
    def test_Transition_Operational_To_Standby(self, virtual_bench, app_lin_com):
        """ Validate the transition of Operational to Standby state
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param app_lin_com: fixture of pytest to use Api LIN of Peak System bench
        :param index: number of repetition
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)
        virtual_bench.ps_generate_por()
        time.sleep(5)

        app_lin_com.start_schedule_table(0)
        time.sleep(2)
        app_lin_com.listMsg = []
        app_lin_com.read(30)
        assert (app_lin_com.linStatus == True)
        current_consumption = virtual_bench.ps_get_current_consumption(
            NI_8012.PS_25V_NEG) + virtual_bench.ps_get_current_consumption(NI_8012.PS_25V_POS)
        assert (current_consumption > oprational_current_conso)

        time.sleep(5)
        app_lin_com.suspend_schedule_table()
        app_lin_com.read(500)  # clean the buffer
        time.sleep(10)  # wait Standby
        app_lin_com.listMsg = []
        app_lin_com.read(20)
        assert (app_lin_com.listMsg == ['Bus Sleep status message'] or [''])
        current_consumption = virtual_bench.ps_get_current_consumption(
            NI_8012.PS_25V_NEG) + virtual_bench.ps_get_current_consumption(NI_8012.PS_25V_POS)
        assert (current_consumption < stantby_current_conso)
        assert (current_consumption < oprational_current_conso)

    def test_Transition_Standby_To_Operational(self, virtual_bench, app_lin_com):
        """
        Validate the transition of Standby to Operational state
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param app_lin_com: fixture of pytest to use Api LIN of Peak System bench
        :param index: number of repetition
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)
        virtual_bench.ps_generate_por()
        time.sleep(15)

        app_lin_com.listMsg = []
        app_lin_com.read(20)
        assert (app_lin_com.listMsg == ['Bus Sleep status message'] or [''])
        current_consumption = virtual_bench.ps_get_current_consumption(
            NI_8012.PS_25V_NEG) + virtual_bench.ps_get_current_consumption(NI_8012.PS_25V_POS)
        assert (current_consumption < stantby_current_conso)
        assert (current_consumption < oprational_current_conso)

        '''Standby to Operational by activating LIN com '''
        app_lin_com.start_schedule_table(0)
        time.sleep(5)
        app_lin_com.listMsg = []
        app_lin_com.read(20)
        assert (app_lin_com.linStatus == True)
        current_consumption = virtual_bench.ps_get_current_consumption(
            NI_8012.PS_25V_NEG) + virtual_bench.ps_get_current_consumption(NI_8012.PS_25V_POS)
        assert (current_consumption > oprational_current_conso)

    def test_Transition_Init_To_Operational(self, virtual_bench, app_lin_com):
        """ Validate the transition of Init to Operational state
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param app_lin_com: fixture of pytest to use Api LIN of Peak System bench
        :param index: number of repetition
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)
        virtual_bench.ps_generate_por()
        time.sleep(5)

        app_lin_com.start_schedule_table(0)
        time.sleep(2)
        app_lin_com.listMsg = []
        app_lin_com.read(30)
        assert (app_lin_com.linStatus == True)
        current_consumption = virtual_bench.ps_get_current_consumption(
            NI_8012.PS_25V_NEG) + virtual_bench.ps_get_current_consumption(NI_8012.PS_25V_POS)
        assert (current_consumption > oprational_current_conso)
        app_lin_com.listMsg = []
        app_lin_com.update_schedule_data(0x3C, [0x1B, 0x02, 0x11, 0x01, 0xFF, 0xFF, 0xFF, 0xFF])
        time.sleep(1)
        app_lin_com.read(500)
        r_received_frame = self.check_Frame_In_Buffer(app_lin_com.listMsg, "0x1b 0x2 0x11 0x1 0xff 0xff 0xff 0xff")
        assert (True == r_received_frame["status"])
        r_received_frame = self.check_Frame_In_Buffer(app_lin_com.listMsg, "0x1b 0x2 0x51 0x1 0x0 0x0 0x0 0x0")
        assert (True == r_received_frame["status"])
        delta = ((int(r_received_frame["TimeStamp"]) - int(r_received_frame["TimeStamp"])) / 1000)
        print("delta ", type(delta), " ", delta)
        assert delta < 100, 'Time has less 100 ms from Init to Ope'

    def test_faster(self):
        data_l = ['0xe', '0x01']
        print(data_l)
        print(int(data_l[1], 16) * (2 ** 8))
        power_sup = int(data_l[0], 16) + (int(data_l[1], 16) * (2 ** 8))
        print("power", power_sup)


        ts = time.time()
        print(time.localtime(ts))
        print(time.localtime(2359277.523))
        print(time.localtime(3221255))


        assert (1 == 1)

    def test_BWC_LIN_Power_Supply(self, virtual_bench, app_lin_com):
        """ Validate Power supply of Lin value [17 to 35]
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param app_lin_com: fixture of pytest to use Api LIN of Peak System bench
        :param index: number of repetition
        :return:
        """
        power_supply_request = range(17, 35, 1)

        self.__set_voltages(virtual_bench, 12.0)
        virtual_bench.ps_generate_por()
        time.sleep(5)
        app_lin_com.start_schedule_table(0)
        time.sleep(2)

        for ps in power_supply_request:
            self.__set_voltages_24v(virtual_bench, 12.0, ps - 12.0)
            app_lin_com.listMsg = []
            app_lin_com.read(150)
            time.sleep(3)
            app_lin_com.listMsg = []
            app_lin_com.read(50)
            for frame in app_lin_com.listMsg:
                print(frame)
            r_received_frame = self.find_ID_Ret_Data(app_lin_com.listMsg, '0x26')

            data_l = r_received_frame["data"].split()
            power_sup = ((int(data_l[0], 16) + (int(data_l[1], 16) * (2 ** 8))) * 0.1)

            assert (ps - 0.5 <= power_sup <= ps + 0.5)


    def test_UDS_Session_Request(self, virtual_bench, app_lin_com):
        """ Validation session request
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param app_lin_com: fixture of pytest to use Api LIN of Peak System bench
        :param index: number of repetition
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)
        virtual_bench.ps_generate_por()
        time.sleep(5)
        app_lin_com.start_schedule_table(0)
        time.sleep(2)
        app_lin_com.listMsg = []
        ts = time.perf_counter()
        print("timeeeeeeeeeeee ",ts )
        app_lin_com.update_schedule_data(0x3C, [0x1B, 0x02, 0x10, 0x60, 0xFF, 0xFF, 0xFF, 0xFF])
        time.sleep(1)
        app_lin_com.read(250)
        for frame in app_lin_com.listMsg:
            print(frame)
        r_received_frame = self.check_Frame_In_Buffer(app_lin_com.listMsg, "0x1b 0x2 0x50 0x60 0x0 0x0 0x0 0x0")
        assert (True == r_received_frame["status"])

    def test_UDS_Session_Request(self, virtual_bench, app_lin_com):
        """ Validation c.	Request Security access
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param app_lin_com: fixture of pytest to use Api LIN of Peak System bench
        :param index: number of repetition
        :return:
        """
        self.__set_voltages(virtual_bench, 12.0)
        virtual_bench.ps_generate_por()
        time.sleep(5)
        app_lin_com.start_schedule_table(0)
        time.sleep(2)
        app_lin_com.update_schedule_data(0x3C, [0x1B, 0x02, 0x10, 0x60, 0xFF, 0xFF, 0xFF, 0xFF])
        time.sleep(1)
        app_lin_com.listMsg = []
        ts = time.time() *1000
        print("timeeeeeeeeeeee ",ts )
        app_lin_com.update_schedule_data(0x3C, [0x1B, 0x02, 0x27, 0x01, 0xFF, 0xFF, 0xFF, 0xFF])
        time.sleep(1)
        app_lin_com.read(250)
        for frame in app_lin_com.listMsg:
            print(frame)
        r_received_frame = self.check_Frame_In_Buffer(app_lin_com.listMsg, "0x1b 0x6 0x67 0x1 0xb5 0x13 0x22 0x0d")
        assert (True == r_received_frame["status"])



    @staticmethod
    def find_ID_Ret_Data(framlist, ID_frame):
        """Find the Id in the buffer and return the data
        return: status"""
        for eachframe in framlist[10:]:
            if eachframe[0] == str(ID_frame):
                return {'status': True, 'data': eachframe[2]}
            else:
                pass
        return {'status': False, 'data': 0}

    @staticmethod
    def check_Frame_In_Buffer(framlist, framedata_expected):
        """Check in the list of frame buffer is the expected frame is recorded
        return: status"""
        for eachframe in framlist:
            if eachframe[2] == str(framedata_expected):
                return {'status': True, 'TimeStamp': eachframe[3]}
            else:
                pass
        return {'status': False, 'TimeStamp': 0}

    @staticmethod
    def __set_voltages_24v(virtual_bench, voltage_POS, voltage_NEG):
        """
        Set both power supply voltages to the same value
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param voltage: voltage to be set
        :return:
        """
        virtual_bench.ps_configure_output(NI_8012.PS_25V_POS, voltage_POS, 0.2)
        virtual_bench.ps_configure_output(NI_8012.PS_25V_NEG, -voltage_NEG, 0.2)

    @staticmethod
    def __set_voltages(virtual_bench, voltage):
        """
        Set both power supply voltages to the same value
        :param virtual_bench: fixture of pytest to use the NI virtual bench
        :param voltage: voltage to be set
        :return:
        """
        virtual_bench.ps_configure_output(NI_8012.PS_25V_POS, voltage, 0.2)
        virtual_bench.ps_configure_output(NI_8012.PS_25V_NEG, -voltage, 0.2)

    @staticmethod
    def execute_bootconsole():
        str = [path + program, argument1, argument2, path + argument3]
        print(str)
        result = subprocess.run([path + program, argument1, argument2, path + argument3]
                                , stdout=PIPE, stderr=STDOUT, shell=True)
        to_print = result.stdout.splitlines()
        print()
        print(to_print)
        print()

        zz = to_print[-1]
        print()
        print(zz)
        print()

        # return str(to_print[-1]).replace('b', '')
        # return str(to_print)
        return (zz.decode('utf-8'))

    @staticmethod
    def initLinCom(appLin_Volvo):
        # appLin_Volvo = Lin_Peak_For_Volvo()
        appLin_Volvo.connect("appLin_Volvo", 1, 1)
        time.sleep(1)
        appLin_Volvo.disconnect()
        time.sleep(1)
        appLin_Volvo.connect("appLin_Volvo", 1, 1)
        appLin_Volvo.set_global_frame_table()
        # appLin_Volvo.get_global_frame_table()
        # appLin_Volvo.displayMenuInput("** Press <enter to stop schedule **")
        time.sleep(1)
        appLin_Volvo.delete_schedule_table(0)
        time.sleep(1)
        appLin_Volvo.set_schedule_table(0)

    @staticmethod
    def LinComOFF(appLin_Volvo):
        # appLin_Volvo.start_schedule_table(0)
        appLin_Volvo.read()

        # appLin_Volvo.suspend_schedule_table()
        appLin_Volvo.delete_schedule_table(0)
        appLin_Volvo.disconnect()
