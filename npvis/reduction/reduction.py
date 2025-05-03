from npvis.element.color import lighten_rgb
class Reduction:

    def __init__(self, problem1, problem2):
        self.problem1 = problem1
        self.problem2 = problem2
        self.input1_to_input2_dict = {}  # map input 1 to set of input 2
        self.highlighted = []  # keep track of highlighted items for resetting

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

    '''
    method to populate input_to_input by adding one pair of correspondance
    '''

    def add_input1_to_input2_by_pair(self, input1, input2):
        if input1 in self.input1_to_input2_dict:
            self.input1_to_input2_dict[input1].add(input2)
        else:
            self.input1_to_input2_dict[input1] = {input2}

    '''
    method to populate input_to_input by connecting one set of input2 to 1
    '''

    def add_input1_to_input2_by_set(self, input1, input2set):
        if input1 in self.input1_to_input2_dict:
            self.input1_to_input2_dict[input1].update(input2set)
        else:
            self.input1_to_input2_dict[input1] = input2set.copy()

    '''
    method to change color according to the clicked set
    '''

    def display_input_to_input(self, clicked_set):
        self.reset_highlighted()
        is_input1 = False
        if len(clicked_set) == 0:
            return
        
        # highlight the clicked set:
        for e in clicked_set:
            e.change_color((255, 0, 0))
            self.highlighted.append(e)
        # CASE: one item in set 
        if len(clicked_set) == 1:
            # if The user click on problem 1 element 
            e1 = next(iter(clicked_set))
            if e1 in self.input1_to_input2_dict:
                is_input1 = True
                for e in self.input1_to_input2_dict[e1]:
                    e.change_color((255, 0, 0))
                    self.highlighted.append(e)
        # CASE: not input 1
        if not is_input1:
            for key, value in self.input1_to_input2_dict.items():
                print(f"clicked set: {clicked_set}")
                print(f"input 1 set: {value}")
                if clicked_set <= value: # clicked set is a subset 
                    print("find input 1")
                    
                    # Note: emperically, a steeper ratio seems help visualization
                    ratio = (1 - len(clicked_set) / len(value)) ** 3
                    lighter_color = lighten_rgb((255, 0, 0), ratio)
                    key.change_color(lighter_color)
                    self.highlighted.append(key)

    def reset_highlighted(self):
        for e in self.highlighted:
            e.change_color(e.default_color)
        self.highlighted = []

    def display_output1_to_output2(self):
        pass

    def display_output2_to_output1(self):
        pass
