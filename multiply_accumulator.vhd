library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;

entity multiply_accumulater is

port(
	input0, input1, input2, input3, input4, input5, input6, input7: IN std_logic_vector(7 downto 0);
	clk, resetb, MCEN: IN std_logic;
	sum: OUT std_logic_vector(15 downto 0);
	--mult_0, mult_1, mult_2, mult_3, sum_0, sum_1 : OUT std_logic_vector(15 downto 0);
	--clock_taken: OUT std_logic_vector(7 downto 0);
	INITIAL_ST, MULT_ST,ADD_ST, MERGE_ST, DONE_ST: OUT std_logic;
	done: OUT std_logic
);

end multiply_accumulater;


architecture multiply_accumulater_RTL of multiply_accumulater is

	type state_type is (INITIAL_STATE, MULT_STATE, ADD_STATE, MERGE_STATE, DONE_STATE);
	
	signal state : state_type;
	
	signal in0, in1, in2, in3, in4, in5, in6, in7 : std_logic_vector(7 downto 0);	--8 input elements
	signal mult0, mult1, mult2, mult3 : std_logic_vector(15 downto 0);	--4 intermedia multiplication results
	signal sum0, sum1 : std_logic_vector(15 downto 0);	--2 intermedia add results & final result
	signal result : std_logic_vector(15 downto 0);
	
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
		variable mult0_temp  : std_logic_vector(15 downto 0);
		variable mult1_temp  : std_logic_vector(15 downto 0);
		variable mult2_temp  : std_logic_vector(15 downto 0);
		variable mult3_temp  : std_logic_vector(15 downto 0);
		variable sum0_temp   : std_logic_vector(15 downto 0);
		variable sum1_temp   : std_logic_vector(15 downto 0);
		variable result_temp : std_logic_vector(15 downto 0);
		
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
			mult0 <= (others => '0');
			mult1 <= (others => '0');
			mult2 <= (others => '0');
			mult3 <= (others => '0');
			sum0 <= (others => '0');
			sum1 <= (others => '0');
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
					mult0 <= (others => '0');
					mult1 <= (others => '0');
					mult2 <= (others => '0');
					mult3 <= (others => '0');
					sum0 <= (others => '0');
					sum1 <= (others => '0');
					result <= (others => '0');
					--clocks_taken_int <= (others => '0');
					
				when MULT_STATE =>
					if(MCEN = '1') then
						mult0_temp := mult0;
						mult1_temp := mult1;
						mult2_temp := mult2;
						mult3_temp := mult3;
						sum0_temp := sum0;
						sum1_temp := sum1;
						result_temp := result;
					
						--clocks_taken_int <= clocks_taken_int + 1;
					
						mult0_temp  := in0 * in1;
						mult1_temp  := in2 * in3;
						mult2_temp  := in4 * in5;
						mult3_temp  := in6 * in7;
						
						mult0 <= mult0_temp;
						mult1 <= mult1_temp;
						mult2 <= mult2_temp;
						mult3 <= mult3_temp;
					
						state <= ADD_STATE;
					end if;
					
				when ADD_STATE =>
					--clocks_taken_int <= clocks_taken_int + 1;
					
					sum0_temp   := mult0_temp + mult1_temp;
					sum1_temp   := mult2_temp + mult3_temp;
					
					sum0 <= sum0_temp;
					sum1 <= sum1_temp;
					
					state <= MERGE_STATE;
					
				when MERGE_STATE =>
					 --clocks_taken_int <= clocks_taken_int + 1;
					
					result_temp := sum0_temp + sum1_temp;
					
					result <= result_temp;
					
					state <= DONE_STATE;
					
				when DONE_STATE =>
					done <= '1';
					state <= INITIAL_STATE;
					
			end case;


		end if;

	end process CU_DPU;


end multiply_accumulater_RTL;
