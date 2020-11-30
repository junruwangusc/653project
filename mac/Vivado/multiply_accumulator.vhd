library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;

entity multiply_accumulater is

port(
	input0, input1, input2, input3, input4, input5, input6, input7, input8, input9, input10, input11, input12, input13, input14, input15: IN std_logic_vector(31 downto 0);
	clk, resetb, MCEN, Finish: IN std_logic;
	sum: OUT std_logic_vector(63 downto 0);
	--mult_0, mult_1, mult_2, mult_3, sum_0, sum_1 : OUT std_logic_vector(15 downto 0);
	--clock_taken: OUT std_logic_vector(7 downto 0);
	INITIAL_ST, MULT_ST, ADD_ST, MERGE_ST, DONE_ST: OUT std_logic;
	done: OUT std_logic
);

end multiply_accumulater;


architecture multiply_accumulater_RTL of multiply_accumulater is

	type state_type is (INITIAL_STATE, MULT_STATE, ADD_STATE, MERGE_STATE, DONE_STATE);
	
	signal state : state_type;
	
	signal in0, in1, in2, in3, in4, in5, in6, in7, in8, in9, in10, in11, in12, in13, in14, in15 : std_logic_vector(31 downto 0);	--8 input elements
	--signal mult0, mult1, mult2, mult3, mult4, mult5, mult6, mult7 : std_logic_vector(63 downto 0);	--4 intermedia multiplication results
	--signal sum1_0, sum1_1, sum1_2, sum1_3, sum2_0, sum2_1 : std_logic_vector(63 downto 0);	--2 intermedia add results & final result
	---signal intermedia_result : std_logic_vector(63 downto 0);
	signal result : std_logic_vector(63 downto 0);
	
	--signal clocks_taken_int : std_logic_vector(7 downto 0);	--total clks needed
	
	
begin 
	
	sum <= result;
	--mult_0 <= mult0;
	--mult_1 <= mult1;
	--mult_2 <= mult2;
	--mult_3 <= mult3;
	--sum_0 <= sum0;
	--sum_1 <= sum1;
	
	--clock_taken <= clocks_taken_int;
	
	INITIAL_ST <= '1' when (state = INITIAL_STATE) else '0'; 
	MULT_ST <= '1' when (state = MULT_STATE) else '0'; 
	ADD_ST <= '1' when (state = ADD_STATE) else '0'; 
	MERGE_ST <= '1' when (state = MERGE_STATE) else '0'; 
	DONE_ST <= '1' when (state = DONE_STATE) else '0'; 

	CU_DPU : process (clk, resetb)
		variable mult0_temp  : std_logic_vector(63 downto 0);
		variable mult1_temp  : std_logic_vector(63 downto 0);
		variable mult2_temp  : std_logic_vector(63 downto 0);
		variable mult3_temp  : std_logic_vector(63 downto 0);
		variable mult4_temp  : std_logic_vector(63 downto 0);
		variable mult5_temp  : std_logic_vector(63 downto 0);
		variable mult6_temp  : std_logic_vector(63 downto 0);
		variable mult7_temp  : std_logic_vector(63 downto 0);
		variable intermedia_result_temp : std_logic_vector(63 downto 0);
		variable result_temp : std_logic_vector(63 downto 0);
		
	begin
	
		if(resetb = '0') then
			state <= INITIAL_STATE;
			in0 <= (others => '-');
			in1 <= (others => '-');
			in2 <= (others => '-');
			in3 <= (others => '-');
			in4 <= (others => '-');
			in5 <= (others => '-');
			in6 <= (others => '-');
			in7 <= (others => '-');
			in8 <= (others => '-');
			in9 <= (others => '-');
			in10 <= (others => '-');
			in11 <= (others => '-');
			in12 <= (others => '-');
			in13 <= (others => '-');
			in14 <= (others => '-');
			in15 <= (others => '-');

			result <= (others => '0');
			
			--clocks_taken_int <= (others => '-');
			done <= '0';
			
		elsif(clk'event and clk = '1') then
			done <= '0';
			
			case(state) is
			
				when INITIAL_STATE =>
					state <= MULT_STATE;
					
					in0 <= input0;
					in1 <= input1;
					in2 <= input2;
					in3 <= input3;
					in4 <= input4;
					in5 <= input5;
					in6 <= input6;
					in7 <= input7;
					in8 <= input8;
					in9 <= input9;
					in10 <= input10;
					in11 <= input11;
					in12 <= input12;
					in13 <= input13;
					in14 <= input14;
					in15 <= input15;

					result <= (others => '0');
					--clocks_taken_int <= (others => '0');
					
				when MULT_STATE =>
					if(MCEN = '1') then

						result_temp := result;
					
						mult0_temp  := in0 * in1;
						mult1_temp  := in2 * in3;
						mult2_temp  := in4 * in5;
						mult3_temp  := in6 * in7;
						mult4_temp  := in8 * in9;
						mult5_temp  := in10 * in11;
						mult6_temp  := in12 * in13;
						mult7_temp  := in14 * in15;
					
						state <= ADD_STATE;
					end if;
					
					
					
				when ADD_STATE =>
					 --clocks_taken_int <= clocks_taken_int + 1;

					intermedia_result_temp := mult0_temp + mult1_temp + mult2_temp + mult3_temp + mult4_temp + mult5_temp + mult6_temp + mult7_temp;
					
					state <= MERGE_STATE;
					
				when MERGE_STATE =>
					if(Finish = '0') then
						result_temp := result_temp + intermedia_result_temp;
						result <= result_temp;
						
						state <= INITIAL_STATE;
					else
						result <= intermedia_result_temp;
						state <= DONE_STATE;
					end if;
					
				when DONE_STATE =>
					done <= '1';
					state <= DONE_STATE;
										
			end case;


		end if;

	end process CU_DPU;


end multiply_accumulater_RTL;
