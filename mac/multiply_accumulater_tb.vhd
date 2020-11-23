library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use STD.textio.all;

entity multiply_accumulater_tb is
end multiply_accumulater_tb;

architecture multiply_accumulater_RTL_tb of multiply_accumulater_tb is

	constant clk_period : time := 10 ns;
	
	signal in0_tb, in1_tb, in2_tb, in3_tb, in4_tb, in5_tb, in6_tb, in7_tb : std_logic_vector(7 downto 0);
	signal clk_tb, resetb_tb, MCEN_tb : std_logic;
	signal mult0_tb, mult1_tb, mult2_tb, mult3_tb : std_logic_vector(15 downto 0);
	signal sum0_tb, sum1_tb : std_logic_vector(15 downto 0);
	signal result_tb : std_logic_vector(15 downto 0);
	
	--signal clocks_taken_tb : std_logic_vector(7 downto 0);
	
	signal INITIAL_ST_tb, MULT_ST_tb, ADD_ST_tb, MERGE_ST_tb, DONE_ST_tb : std_logic;
	
	signal done_tb : std_logic;
	
	--signal clock_count : integer range 0 to 9999;
	signal test_num: integer range 0 to 100;

	component multiply_accumulater
		port(
			input0, input1, input2, input3, input4, input5, input6, input7: IN std_logic_vector(7 downto 0);
			clk, resetb, MCEN: IN std_logic;
			sum: OUT std_logic_vector(15 downto 0);
			--mult_0, mult_1, mult_2, mult_3, sum_0, sum_1 : OUT std_logic_vector(15 downto 0);
			--clock_taken: OUT std_logic_vector(7 downto 0);
			INITIAL_ST, MULT_ST,ADD_ST, MERGE_ST, DONE_ST: OUT std_logic;
			done: OUT std_logic
		);
	end component;

begin
	
	UUT : multiply_accumulater
		port map(
			in0_tb, in1_tb, in2_tb, in3_tb, in4_tb, in5_tb, in6_tb, in7_tb,
			clk_tb, resetb_tb, MCEN_tb,
			result_tb,
			--mult0_tb, mult1_tb, mult2_tb, mult3_tb, sum0_tb, sum1_tb,
			--clocks_taken_tb,
			INITIAL_ST_tb, MULT_ST_tb, ADD_ST_tb, MERGE_ST_tb, DONE_ST_tb,
			done_tb
		);
	
	MCEN_tb  <= '1';
	resetb_tb <= '0', '1' after (clk_period * 2.1);
	
	clock_generation : process
	begin
		clk_tb <= '0', '1' after(clk_period/2);
		wait for clk_period;
	end process clock_generation;
	
	--clock_counting : process (clk_tb, resetb_tb)
	--begin
		--if (resetb_tb = '0') then
		--	clock_count <= 0;
		--elsif clk_tb'event and clk_tb = '1' then
		--	clock_count <= clock_count + 1;
		--end if;
	--end process clock_counting;
	
	
		Stim_multiply_accumulater: process
			--file out_file : TEXT open WRITE_MODE is "output_results.txt" ;
			--variable out_line: line;
			
			procedure apply_test (constant in0_value, in1_value, in2_value, in3_value, in4_value, in5_value, in6_value, in7_value : in integer) is
			begin
				in0_tb <= CONV_STD_LOGIC_VECTOR(in0_value, 8);
				in1_tb <= CONV_STD_LOGIC_VECTOR(in1_value, 8);
				in2_tb <= CONV_STD_LOGIC_VECTOR(in2_value, 8);
				in3_tb <= CONV_STD_LOGIC_VECTOR(in3_value, 8);
				in4_tb <= CONV_STD_LOGIC_VECTOR(in4_value, 8);
				in5_tb <= CONV_STD_LOGIC_VECTOR(in5_value, 8);
				in6_tb <= CONV_STD_LOGIC_VECTOR(in6_value, 8);
				in7_tb <= CONV_STD_LOGIC_VECTOR(in7_value, 8);
				
				test_num <= test_num + 1;
				
				wait until clk_tb'event and clk_tb = '1';
				wait for 1 ns;
				wait until (done_tb'event and done_tb = '1');
				wait for 1 ns;
				wait until clk_tb'event and clk_tb = '1';
				wait for 3 ns;
	
				--WRITE(out_line, string'("Test #"));
				--WRITE(out_line, test_num);
				--WRITELINE(out_file, out_line);
	
				--WRITE(out_line, string'("input0 = "));
				--WRITE(out_line, in0_value);
				--WRITE(out_line, string'(", input1 = "));
				--WRITE(out_line, in1_value);
				--WRITE(out_line, string'(", input2 = "));
				--WRITE(out_line, in2_value);
				--WRITE(out_line, string'(", input3 = "));
				--WRITE(out_line, in3_value);
				--WRITE(out_line, string'(", input4 = "));
				--WRITE(out_line, in4_value);
				--WRITE(out_line, string'(", input5 = "));
				--WRITE(out_line, in5_value);
				--WRITE(out_line, string'(", input6 = "));
				--WRITE(out_line, in6_value);
				--WRITE(out_line, string'(", input7 = "));
				--WRITE(out_line, in7_value);
				--WRITELINE(out_file, out_line);
				
				--WRITE(out_line, string'(", mult0 = "));
				--WRITE(out_line, CONV_INTEGER(unsigned(mult0_tb)));
				--WRITE(out_line, string'(", mult1 = "));
				--WRITE(out_line, CONV_INTEGER(unsigned(mult1_tb)));
				--WRITE(out_line, string'(", mult2 = "));
				--WRITE(out_line, CONV_INTEGER(unsigned(mult2_tb)));
				--WRITE(out_line, string'(", mult3 = "));
				--WRITE(out_line, CONV_INTEGER(unsigned(mult3_tb)));
				--WRITE(out_line, string'(", sum0 = "));
				--WRITE(out_line, CONV_INTEGER(unsigned(sum0_tb)));
				--WRITE(out_line, string'(", sum1 = "));
				--WRITE(out_line, CONV_INTEGER(unsigned(sum1_tb)));
				--WRITE(out_line, string'(", merge result = "));
				--WRITE(out_line, CONV_INTEGER(unsigned(result_tb)));
				--WRITELINE(out_file, out_line);
	
				--WRITE(out_line, string'("Number of Clocks taken = "));
				--WRITE(out_line, CONV_INTEGER(unsigned(clocks_taken_tb)));
				--WRITELINE(out_file, out_line);
				--WRITE(out_line , ' '); -- blank line
				--WRITELINE(out_file, out_line);
			end procedure apply_test;
		
		begin
			--initial values
			in0_tb <= CONV_STD_LOGIC_VECTOR(0, 8);
			in1_tb <= CONV_STD_LOGIC_VECTOR(0, 8);
			in2_tb <= CONV_STD_LOGIC_VECTOR(0, 8);
			in3_tb <= CONV_STD_LOGIC_VECTOR(0, 8);
			in4_tb <= CONV_STD_LOGIC_VECTOR(0, 8);
			in5_tb <= CONV_STD_LOGIC_VECTOR(0, 8);
			in6_tb <= CONV_STD_LOGIC_VECTOR(0, 8);
			in7_tb <= CONV_STD_LOGIC_VECTOR(0, 8);
			
			test_num <= 0;
			
			wait for (clk_period *2);
			
			apply_test (78,48,29,39,23,25,67,83); -- Test #1
			apply_test (107,235,245,166,177,245,243,130); -- Test #2
			apply_test (51,25,44,78,82,77,34,59); -- Test #3
			apply_test (254,164,163,63,126,239,97,164); -- Test #4
			apply_test (253,64,234,167,87,185,238,216); -- Test #5

			--WRITE(out_line , string'("All tests concluded."));
			--WRITELINE(out_file, out_line);
			
			wait;
	
		end process Stim_multiply_accumulater;
	
end multiply_accumulater_RTL_tb;
