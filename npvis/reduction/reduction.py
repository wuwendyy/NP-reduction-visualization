class Reduction:

    def __init__(self, problem1, problem2):
        self.problem1 = problem1
        self.problem2 = problem2
        self.input1_to_input2_pairs = [] #ref_to_ref pairs
        self.output1_to_output2_pairs = []
        self.output2_to_output1_pairs = []
        self.input1_to_input2_dict = {}
        self.output1_to_output2_pairs_dict = {}
        self.output2_to_output1_pairs_dict = {}
        

    '''
    method to populate input_to_input_pairs list
    '''
    def input1_to_input2(self):
        pass

    '''
    method to populate output1_to_output2_pairs list
    '''
    def solution1_to_solution2(self):
        pass

    '''
    method to populate output2_to_output1_pairs list
    '''
    def solution2_to_solution1(self):
        pass

    def display_input_to_input(self, clicked_helper):
        if clicked_helper is not None:
            # The user click on problem 1 element 
            clicked_helper.change_color((0, 255, 0))
            # Loop to see all colors that need change:
            for (e1,e2) in self.input1_to_input2_pairs:
                if e1 == clicked_helper:
                    e2.change_color((0, 255, 0))
                elif e2 == clicked_helper:
                    e1.change_color((0, 255, 0))
    

    def display_output1_to_output2(self):
        pass

    def display_output2_to_output1(self):
        pass
